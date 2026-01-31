"""Tasks for aggregating analytics data."""
import logging
from datetime import timedelta

from celery import shared_task
from django.db.models import Count, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    name='analytics.aggregate_daily_stats',
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def aggregate_daily_stats(self, date_str: str | None = None) -> dict:
    """
    Агрегирует статистику за день.

    Запускается каждую ночь для агрегации данных за предыдущий день.
    Можно запустить вручную с указанием конкретной даты.

    Args:
        date_str: Дата в формате 'YYYY-MM-DD' (по умолчанию - вчера)

    Returns:
        Словарь с агрегированными данными
    """
    from apps.analytics.models import AnalyticsEvent, DailyStats, EventType
    from apps.orders.models import Order
    from apps.users.models import User

    # Определяем дату
    if date_str:
        from datetime import datetime
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = (timezone.now() - timedelta(days=1)).date()

    # Считаем новых пользователей
    new_users = User.objects.filter(
        date_joined__date=target_date
    ).count()

    # Считаем активных пользователей (DAU)
    # Учитываем авторизованных пользователей
    auth_users = AnalyticsEvent.objects.filter(
        event_date=target_date,
        user__isnull=False
    ).values('user').distinct().count()

    # Учитываем анонимных по session_id
    anon_sessions = AnalyticsEvent.objects.filter(
        event_date=target_date,
        user__isnull=True,
        session_id__gt=''  # Непустой session_id
    ).values('session_id').distinct().count()

    active_users = auth_users + anon_sessions

    # Агрегируем события
    events_agg = AnalyticsEvent.objects.filter(
        event_date=target_date
    ).values('event_type').annotate(
        count=Count('id')
    )

    events_dict = {item['event_type']: item['count'] for item in events_agg}

    # Считаем заказы и выручку
    orders_data = Order.objects.filter(
        created_at__date=target_date
    ).aggregate(
        orders_count=Count('id'),
        total_revenue=Sum('total')
    )

    # Создаём или обновляем запись
    stats, created = DailyStats.objects.update_or_create(
        date=target_date,
        defaults={
            'new_users': new_users,
            'active_users': active_users,
            'total_events': sum(events_dict.values()),
            'product_views': events_dict.get(EventType.PRODUCT_VIEW, 0),
            'product_clicks': events_dict.get(EventType.PRODUCT_CLICK, 0),
            'cart_adds': events_dict.get(EventType.CART_ADD, 0),
            'cart_removes': events_dict.get(EventType.CART_REMOVE, 0),
            'searches': events_dict.get(EventType.SEARCH, 0),
            'orders': orders_data['orders_count'] or 0,
            'revenue': orders_data['total_revenue'] or 0,
        }
    )

    logger.info(
        "Daily stats aggregated: date=%s new_users=%d active=%d orders=%d revenue=%d",
        target_date,
        new_users,
        active_users,
        orders_data['orders_count'] or 0,
        orders_data['total_revenue'] or 0,
    )

    return {
        'date': str(target_date),
        'created': created,
        'new_users': new_users,
        'active_users': active_users,
        'orders': orders_data['orders_count'] or 0,
        'revenue': orders_data['total_revenue'] or 0,
    }


@shared_task(
    name='analytics.cleanup_old_events',
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def cleanup_old_events(self, days: int = 90) -> dict:
    """
    Удаляет старые события аналитики.

    Args:
        days: Количество дней хранения (по умолчанию 90)

    Returns:
        Словарь с количеством удалённых записей
    """
    from apps.analytics.models import AnalyticsEvent

    cutoff_date = (timezone.now() - timedelta(days=days)).date()

    deleted_count, _ = AnalyticsEvent.objects.filter(
        event_date__lt=cutoff_date
    ).delete()

    logger.info("Analytics cleanup: deleted=%d cutoff=%s", deleted_count, cutoff_date)

    return {
        'deleted_count': deleted_count,
        'cutoff_date': str(cutoff_date),
        'days': days,
    }
