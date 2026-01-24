"""
Broadcaster service for sending mass messages.
"""
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from telegram import Bot
from telegram.error import TelegramError, Forbidden, RetryAfter

from apps.bot.models import Broadcast, BroadcastContentType


logger = logging.getLogger(__name__)


class SendResult(Enum):
    """Result of sending a message."""
    SUCCESS = 'success'
    BLOCKED = 'blocked'
    FAILED = 'failed'


@dataclass
class SendOutcome:
    """Outcome of a send attempt."""
    result: SendResult
    error_message: str = ''


class BroadcastSender:
    """
    Service for sending broadcast messages to users.

    Handles rate limiting (30 msg/sec for Telegram API).
    """

    # Telegram rate limit: 30 messages per second
    BATCH_SIZE = 25
    BATCH_DELAY = 1.0  # seconds between batches

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_to_user(
        self,
        telegram_id: int,
        broadcast: Broadcast,
    ) -> SendOutcome:
        """
        Send broadcast message to a single user.

        Returns SendOutcome with result and optional error message.
        """
        try:
            await self._send_content(telegram_id, broadcast)
            return SendOutcome(result=SendResult.SUCCESS)

        except Forbidden as e:
            # User blocked the bot
            logger.info(f"User {telegram_id} blocked the bot: {e}")
            return SendOutcome(
                result=SendResult.BLOCKED,
                error_message=str(e),
            )

        except RetryAfter as e:
            # Rate limited, wait and retry
            logger.warning(f"Rate limited, waiting {e.retry_after} seconds")
            await asyncio.sleep(e.retry_after)
            return await self.send_to_user(telegram_id, broadcast)

        except TelegramError as e:
            logger.error(f"Failed to send to {telegram_id}: {e}")
            return SendOutcome(
                result=SendResult.FAILED,
                error_message=str(e),
            )

    async def _send_content(self, telegram_id: int, broadcast: Broadcast) -> None:
        """Send content based on broadcast type."""
        content_type = broadcast.content_type
        text = broadcast.text or None
        file_id = broadcast.file_id or None

        if content_type == BroadcastContentType.TEXT:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=text,
            )

        elif content_type == BroadcastContentType.PHOTO:
            await self.bot.send_photo(
                chat_id=telegram_id,
                photo=file_id,
                caption=text,
            )

        elif content_type == BroadcastContentType.VIDEO:
            await self.bot.send_video(
                chat_id=telegram_id,
                video=file_id,
                caption=text,
            )

        elif content_type == BroadcastContentType.DOCUMENT:
            await self.bot.send_document(
                chat_id=telegram_id,
                document=file_id,
                caption=text,
            )

        elif content_type == BroadcastContentType.VOICE:
            await self.bot.send_voice(
                chat_id=telegram_id,
                voice=file_id,
            )
