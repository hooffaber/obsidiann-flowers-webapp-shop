"""Cleanup tasks for products app."""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    name='products.cleanup_old_favorite_actions',
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def cleanup_old_favorite_actions(self, days: int = 90) -> dict:
    """
    Удаляет старые записи из истории избранного.

    Args:
        days: Количество дней, после которых записи удаляются (по умолчанию 90)

    Returns:
        Словарь с количеством удалённых записей
    """
    from apps.products.models import FavoriteAction

    cutoff_date = timezone.now() - timedelta(days=days)

    # Удаляем записи старше cutoff_date
    deleted_count, _ = FavoriteAction.objects.filter(
        created_at__lt=cutoff_date
    ).delete()

    logger.info("Favorites cleanup: deleted=%d cutoff=%s", deleted_count, cutoff_date.date())

    return {
        'deleted_count': deleted_count,
        'cutoff_date': cutoff_date.isoformat(),
        'days': days,
    }
