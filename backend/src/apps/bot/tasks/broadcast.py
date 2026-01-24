"""
Celery tasks for broadcast sending.
"""
import logging
import time

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.bot.models import (
    Broadcast,
    BroadcastLog,
    BroadcastLogStatus,
    BroadcastStatus,
    BroadcastContentType,
)
from apps.users.models import User


logger = logging.getLogger(__name__)

# Telegram rate limit: ~30 messages per second
BATCH_SIZE = 25
BATCH_DELAY = 1.0  # seconds


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='bot.send_broadcast',
)
def send_broadcast_task(self, broadcast_id: int) -> dict:
    """
    Send broadcast to users by their usernames.

    Uses synchronous requests to Telegram API.
    """
    try:
        broadcast = Broadcast.objects.get(id=broadcast_id)
    except Broadcast.DoesNotExist:
        logger.error(f"Broadcast {broadcast_id} not found")
        return {'error': 'Broadcast not found'}

    # Update status to sending
    broadcast.status = BroadcastStatus.SENDING
    broadcast.started_at = timezone.now()
    broadcast.save(update_fields=['status', 'started_at'])

    # Get users by usernames (search in both telegram_username and username fields)
    from django.db.models import Q

    usernames = broadcast.recipients_usernames or []
    # Build OR query for each username
    if usernames:
        q = Q()
        for uname in usernames:
            q |= Q(telegram_username__iexact=uname) | Q(username__iexact=uname)
        users = list(
            User.objects.filter(q, telegram_id__isnull=False)
            .values_list('id', 'telegram_id', 'username')
        )
    else:
        users = []

    total_recipients = len(users)
    broadcast.total_recipients = total_recipients
    broadcast.save(update_fields=['total_recipients'])

    if total_recipients == 0:
        broadcast.status = BroadcastStatus.COMPLETED
        broadcast.completed_at = timezone.now()
        broadcast.save(update_fields=['status', 'completed_at'])
        return {'total': 0, 'sent': 0, 'failed': 0, 'blocked': 0}

    # Create log entries for all recipients
    logs_to_create = [
        BroadcastLog(
            broadcast=broadcast,
            user_id=user_id,
            telegram_id=telegram_id,
            status=BroadcastLogStatus.PENDING,
        )
        for user_id, telegram_id, _ in users
    ]
    BroadcastLog.objects.bulk_create(logs_to_create, batch_size=1000)

    # Send messages
    stats = _send_broadcast_sync(broadcast)

    # Update broadcast statistics
    broadcast.sent_count = stats['sent']
    broadcast.failed_count = stats['failed'] + stats['blocked']
    broadcast.status = BroadcastStatus.COMPLETED
    broadcast.completed_at = timezone.now()
    broadcast.save(update_fields=[
        'sent_count',
        'failed_count',
        'status',
        'completed_at',
    ])

    logger.info(
        f"Broadcast {broadcast_id} completed: "
        f"sent={stats['sent']}, failed={stats['failed']}, blocked={stats['blocked']}"
    )

    return stats


def _send_broadcast_sync(broadcast: Broadcast) -> dict:
    """Send broadcast messages synchronously."""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    base_url = f"https://api.telegram.org/bot{bot_token}"

    stats = {'sent': 0, 'failed': 0, 'blocked': 0}

    # Get pending logs
    logs = BroadcastLog.objects.filter(
        broadcast=broadcast,
        status=BroadcastLogStatus.PENDING,
    )

    count = 0
    for log in logs.iterator():
        result = _send_message(base_url, log.telegram_id, broadcast)

        if result == 'success':
            log.status = BroadcastLogStatus.SENT
            log.sent_at = timezone.now()
            stats['sent'] += 1
        elif result == 'blocked':
            log.status = BroadcastLogStatus.BLOCKED
            log.error_message = 'User blocked the bot'
            stats['blocked'] += 1
        else:
            log.status = BroadcastLogStatus.FAILED
            log.error_message = result
            stats['failed'] += 1

        log.save(update_fields=['status', 'error_message', 'sent_at'])

        count += 1
        # Rate limiting
        if count % BATCH_SIZE == 0:
            time.sleep(BATCH_DELAY)

    return stats


def _send_message(base_url: str, chat_id: int, broadcast: Broadcast) -> str:
    """
    Send a single message to Telegram.

    Returns 'success', 'blocked', or error message.
    """
    content_type = broadcast.content_type
    text = broadcast.text or None
    file_id = broadcast.file_id or None

    try:
        if content_type == BroadcastContentType.TEXT:
            response = requests.post(
                f"{base_url}/sendMessage",
                json={'chat_id': chat_id, 'text': text},
                timeout=30,
            )

        elif content_type == BroadcastContentType.PHOTO:
            data = {'chat_id': chat_id, 'photo': file_id}
            if text:
                data['caption'] = text
            response = requests.post(
                f"{base_url}/sendPhoto",
                json=data,
                timeout=30,
            )

        elif content_type == BroadcastContentType.VIDEO:
            data = {'chat_id': chat_id, 'video': file_id}
            if text:
                data['caption'] = text
            response = requests.post(
                f"{base_url}/sendVideo",
                json=data,
                timeout=30,
            )

        elif content_type == BroadcastContentType.DOCUMENT:
            data = {'chat_id': chat_id, 'document': file_id}
            if text:
                data['caption'] = text
            response = requests.post(
                f"{base_url}/sendDocument",
                json=data,
                timeout=30,
            )

        elif content_type == BroadcastContentType.VOICE:
            response = requests.post(
                f"{base_url}/sendVoice",
                json={'chat_id': chat_id, 'voice': file_id},
                timeout=30,
            )

        else:
            return f"Unknown content type: {content_type}"

        # Check response
        if response.status_code == 200:
            return 'success'

        result = response.json()
        error_code = result.get('error_code')
        description = result.get('description', 'Unknown error')

        # User blocked the bot or chat not found
        if error_code in (403, 400):
            if 'blocked' in description.lower() or 'chat not found' in description.lower():
                return 'blocked'

        return description

    except requests.exceptions.Timeout:
        return 'Request timeout'
    except requests.exceptions.RequestException as e:
        return str(e)
