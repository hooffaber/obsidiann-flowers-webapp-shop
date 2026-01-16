"""Analytics event model."""
from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class EventType(models.TextChoices):
    """Типы событий аналитики."""
    # Сессии
    APP_OPEN = 'app_open', 'Открытие приложения'

    # Товары
    PRODUCT_VIEW = 'product_view', 'Просмотр товара'
    PRODUCT_CLICK = 'product_click', 'Клик на товар'

    # Корзина
    CART_ADD = 'cart_add', 'Добавление в корзину'
    CART_REMOVE = 'cart_remove', 'Удаление из корзины'

    # Категории
    CATEGORY_VIEW = 'category_view', 'Просмотр категории'

    # Поиск
    SEARCH = 'search', 'Поисковый запрос'

    # Заказы
    CHECKOUT_START = 'checkout_start', 'Начало оформления'
    ORDER_COMPLETE = 'order_complete', 'Заказ оформлен'


class AnalyticsEvent(TimeStampedModel):
    """
    Универсальная модель для хранения событий аналитики.

    Позволяет отслеживать:
    - Просмотры и клики по товарам
    - Добавления/удаления из корзины
    - Поисковые запросы
    - Переходы по категориям
    - Сессии пользователей
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics_events',
        verbose_name='Пользователь',
        null=True,
        blank=True,  # Для анонимных пользователей
    )

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        verbose_name='Тип события',
        db_index=True,
    )

    # Связи с объектами (опциональные)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_events',
        verbose_name='Товар',
    )

    category = models.ForeignKey(
        'products.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analytics_events',
        verbose_name='Категория',
    )

    # Дополнительные данные
    search_query = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Поисковый запрос',
    )

    # Метаданные (JSON для гибкости)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Метаданные',
        help_text='Дополнительные данные события (цена, количество и т.д.)',
    )

    # Для группировки по дням (денормализация для быстрых запросов)
    event_date = models.DateField(
        verbose_name='Дата события',
        db_index=True,
    )

    # Идентификатор сессии (для анонимных пользователей)
    session_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        verbose_name='ID сессии',
    )

    class Meta:
        verbose_name = 'Событие аналитики'
        verbose_name_plural = 'События аналитики'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'event_date']),
            models.Index(fields=['user', 'event_date']),
            models.Index(fields=['product', 'event_type']),
            models.Index(fields=['category', 'event_type']),
            models.Index(fields=['event_date', 'event_type']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else f'session:{self.session_id[:8]}'
        return f'{user_str} - {self.get_event_type_display()}'

    def save(self, *args, **kwargs):
        # Автоматически заполняем event_date
        if not self.event_date:
            from django.utils import timezone
            self.event_date = timezone.now().date()
        super().save(*args, **kwargs)


class DailyStats(models.Model):
    """
    Агрегированная статистика по дням.

    Заполняется Celery-задачей для быстрого доступа к метрикам.
    """

    date = models.DateField(
        unique=True,
        verbose_name='Дата',
        db_index=True,
    )

    # Пользователи
    new_users = models.PositiveIntegerField(
        default=0,
        verbose_name='Новых пользователей',
    )
    active_users = models.PositiveIntegerField(
        default=0,
        verbose_name='Активных пользователей (DAU)',
    )

    # События
    total_events = models.PositiveIntegerField(
        default=0,
        verbose_name='Всего событий',
    )
    product_views = models.PositiveIntegerField(
        default=0,
        verbose_name='Просмотров товаров',
    )
    product_clicks = models.PositiveIntegerField(
        default=0,
        verbose_name='Кликов на товары',
    )
    cart_adds = models.PositiveIntegerField(
        default=0,
        verbose_name='Добавлений в корзину',
    )
    cart_removes = models.PositiveIntegerField(
        default=0,
        verbose_name='Удалений из корзины',
    )
    searches = models.PositiveIntegerField(
        default=0,
        verbose_name='Поисковых запросов',
    )
    orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Заказов',
    )

    # Финансы
    revenue = models.PositiveIntegerField(
        default=0,
        verbose_name='Выручка (копейки)',
    )

    # Метаданные
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено',
    )

    class Meta:
        verbose_name = 'Дневная статистика'
        verbose_name_plural = 'Дневная статистика'
        ordering = ['-date']

    def __str__(self):
        return f'Статистика за {self.date}'

    @property
    def revenue_display(self) -> str:
        """Выручка для отображения."""
        return f"{self.revenue // 100:,}".replace(',', ' ') + ' ₽'
