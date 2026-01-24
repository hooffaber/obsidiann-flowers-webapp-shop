"""
Celery tasks for order notifications.
"""
import logging
from celery import shared_task

from apps.bot.services.notifications import send_order_notification

logger = logging.getLogger(__name__)


@shared_task(
    name='bot.send_order_notification',
    max_retries=3,
    default_retry_delay=30,
)
def send_order_notification_task(
    telegram_id: int,
    order_id: int,
    items: list[dict],
    total: int,
    delivery_fee: int,
    delivery_address: str,
    delivery_date: str | None = None,
    delivery_time: str | None = None,
) -> bool:
    """
    Celery task to send order notification.
    """
    return send_order_notification(
        telegram_id=telegram_id,
        order_id=order_id,
        items=items,
        total=total,
        delivery_fee=delivery_fee,
        delivery_address=delivery_address,
        delivery_date=delivery_date,
        delivery_time=delivery_time,
    )
