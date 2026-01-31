"""
Celery tasks for order notifications.
"""
import logging
from celery import shared_task

from apps.bot.services.notifications import send_order_notification, send_admin_order_notification

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
    result = send_order_notification(
        telegram_id=telegram_id,
        order_id=order_id,
        items=items,
        total=total,
        delivery_fee=delivery_fee,
        delivery_address=delivery_address,
        delivery_date=delivery_date,
        delivery_time=delivery_time,
    )

    if result:
        logger.info("Order notification sent: order=%s tg_id=%s", order_id, telegram_id)
    else:
        logger.warning("Order notification failed: order=%s tg_id=%s", order_id, telegram_id)

    return result


@shared_task(
    name='bot.send_admin_order_notification',
    max_retries=3,
    default_retry_delay=30,
)
def send_admin_order_notification_task(
    order_id: int,
    items: list[dict],
    total: int,
    delivery_fee: int,
    delivery_address: str,
    customer_name: str,
    customer_username: str | None = None,
    customer_phone: str | None = None,
    delivery_date: str | None = None,
    delivery_time: str | None = None,
) -> int:
    """
    Celery task to send order notification to admins.
    """
    result = send_admin_order_notification(
        order_id=order_id,
        items=items,
        total=total,
        delivery_fee=delivery_fee,
        delivery_address=delivery_address,
        customer_name=customer_name,
        customer_username=customer_username,
        customer_phone=customer_phone,
        delivery_date=delivery_date,
        delivery_time=delivery_time,
    )

    logger.info("Admin order notification task completed: order=%s admins_notified=%s", order_id, result)
    return result
