"""
Django signals for order status change notifications.
"""
import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.orders.models import Order, OrderStatus

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def track_status_change(sender, instance, **kwargs):
    """
    Track the old status before saving.
    """
    if instance.pk:
        old_status = Order.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
        instance._old_status = old_status
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def notify_status_change(sender, instance, created, **kwargs):
    """
    Send notification when order status changes.
    """
    if created:
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status is None:
        return

    if old_status == instance.status:
        return

    # Don't notify for transition to 'new' (only happens on creation)
    if instance.status == OrderStatus.NEW:
        return

    # Get user's telegram_id
    telegram_id = getattr(instance.user, 'telegram_id', None)
    if not telegram_id:
        logger.warning(
            "Cannot send status notification for order #%s: user has no telegram_id",
            instance.pk
        )
        return

    # Get status display name
    status_display = instance.get_status_display()

    # Send notification via Celery
    from apps.bot.tasks import send_order_status_notification_task

    send_order_status_notification_task.delay(
        telegram_id=telegram_id,
        order_id=instance.pk,
        new_status=instance.status,
        status_display=status_display,
    )

    logger.info(
        "Order status notification queued: order=#%s status=%s->%s",
        instance.pk,
        old_status,
        instance.status,
    )
