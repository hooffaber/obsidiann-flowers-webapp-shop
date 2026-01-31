"""
Celery tasks for order notifications.
"""
import logging
from celery import shared_task

from apps.bot.services.notifications import (
    send_order_notification,
    send_admin_order_notification,
    send_order_status_notification,
)

logger = logging.getLogger(__name__)


@shared_task(
    name='bot.send_order_notification',
    max_retries=3,
    default_retry_delay=30,
)
def send_order_notification_task(
    telegram_id: int,
    order_uid: str,
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
        order_uid=order_uid,
        items=items,
        total=total,
        delivery_fee=delivery_fee,
        delivery_address=delivery_address,
        delivery_date=delivery_date,
        delivery_time=delivery_time,
    )

    if result:
        logger.info("Order notification sent: order=%s tg_id=%s", order_uid, telegram_id)
    else:
        logger.warning("Order notification failed: order=%s tg_id=%s", order_uid, telegram_id)

    return result


@shared_task(
    name='bot.send_admin_order_notification',
    max_retries=3,
    default_retry_delay=30,
)
def send_admin_order_notification_task(
    order_uid: str,
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
        order_uid=order_uid,
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

    logger.info("Admin order notification task completed: order=%s admins_notified=%s", order_uid, result)
    return result


@shared_task(
    name='bot.send_order_status_notification',
    max_retries=3,
    default_retry_delay=30,
)
def send_order_status_notification_task(order_id: int) -> bool:
    """
    Celery task to send order status change notification.
    """
    from apps.orders.models import Order

    try:
        order = Order.objects.select_related('user').prefetch_related('items').get(pk=order_id)
    except Order.DoesNotExist:
        logger.error("Order not found: order_id=%s", order_id)
        return False

    telegram_id = getattr(order.user, 'telegram_id', None)
    if not telegram_id:
        logger.warning("Cannot send status notification: user has no telegram_id, order=%s", order.uid)
        return False

    # Build items list
    items = [
        {
            'title': item.product_title,
            'qty': item.qty,
            'line_total': item.line_total,
        }
        for item in order.items.all()
    ]

    # Format delivery date
    order_date = order.created_at.strftime('%d.%m.%Y') if order.created_at else None

    # Get telegram username if available
    telegram_username = getattr(order.user, 'telegram_username', None) or None

    result = send_order_status_notification(
        telegram_id=telegram_id,
        order_uid=order.uid,
        new_status=order.status,
        status_display=order.get_status_display(),
        customer_phone=order.customer_phone,
        customer_username=telegram_username,
        order_date=order_date,
        items=items,
    )

    if result:
        logger.info("Status notification sent: order=%s status=%s tg_id=%s", order.uid, order.status, telegram_id)
    else:
        logger.warning("Status notification failed: order=%s status=%s tg_id=%s", order.uid, order.status, telegram_id)

    return result
