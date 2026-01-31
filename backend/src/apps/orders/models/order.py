"""Order models."""
import random

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


def generate_order_uid():
    """Генерирует уникальный 6-значный UID."""
    from apps.orders.models import Order
    while True:
        uid = str(random.randint(100000, 999999))
        if not Order.objects.filter(uid=uid).exists():
            return uid


class OrderStatus(models.TextChoices):
    """Статусы заказа."""
    NEW = 'new', 'Новый'
    CONFIRMED = 'confirmed', 'Подтверждён'
    IN_PROGRESS = 'in_progress', 'Готовится'
    DELIVERING = 'delivering', 'Доставляется'
    DONE = 'done', 'Выполнен'
    CANCELLED = 'cancelled', 'Отменён'


class PaymentMethod(models.TextChoices):
    """Способы оплаты."""
    LINK_AFTER_ORDER = 'link_after_order', 'Ссылка на оплату после заказа'
    # В будущем можно добавить:
    # CARD_ONLINE = 'card_online', 'Картой онлайн'
    # CASH = 'cash', 'Наличными курьеру'
    # CARD_ON_DELIVERY = 'card_on_delivery', 'Картой курьеру'


class Order(TimeStampedModel):
    """
    Заказ.

    Содержит данные клиента, доставки и суммы.
    Позиции — в OrderItem.
    """

    uid = models.CharField(
        max_length=10,
        unique=True,
        default=generate_order_uid,
        verbose_name='Номер заказа',
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Пользователь',
    )
    status = models.CharField(
        max_length=24,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name='Статус',
        db_index=True,
    )
    payment_method = models.CharField(
        max_length=32,
        choices=PaymentMethod.choices,
        default=PaymentMethod.LINK_AFTER_ORDER,
        verbose_name='Способ оплаты',
    )

    # === Суммы (в копейках) ===
    subtotal = models.PositiveIntegerField(
        default=0,
        verbose_name='Сумма товаров (копейки)',
    )
    delivery_fee = models.PositiveIntegerField(
        default=0,
        verbose_name='Стоимость доставки (копейки)',
    )
    discount = models.PositiveIntegerField(
        default=0,
        verbose_name='Скидка (копейки)',
    )
    total = models.PositiveIntegerField(
        default=0,
        verbose_name='Итого (копейки)',
    )

    # === Контактные данные ===
    customer_name = models.CharField(
        max_length=120,
        verbose_name='Имя получателя',
    )
    customer_phone = models.CharField(
        max_length=32,
        verbose_name='Телефон',
    )

    # === Доставка ===
    delivery_address = models.CharField(
        max_length=255,
        verbose_name='Адрес доставки',
    )
    delivery_comment = models.TextField(
        blank=True,
        verbose_name='Комментарий',
        help_text='Домофон, подъезд, особые пожелания',
    )
    delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата доставки',
    )
    delivery_time_from = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Время с',
    )
    delivery_time_to = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Время до',
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.uid} - {self.customer_name}"

    @property
    def total_display(self) -> str:
        """Итого для отображения."""
        return f"{self.total // 100:,}".replace(',', ' ') + ' ₽'

    def calculate_totals(self):
        """Пересчитать суммы из позиций."""
        self.subtotal = sum(
            item.line_total for item in self.items.all()
        )
        self.total = self.subtotal + self.delivery_fee - self.discount


class OrderItem(TimeStampedModel):
    """
    Позиция заказа.

    ВАЖНО: Храним snapshot данных на момент заказа!
    Если товар изменится/удалится — заказ останется корректным.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ',
    )

    # === Ссылки (для аналитики, могут стать NULL) ===
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='Товар',
    )

    qty = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество',
    )

    # === SNAPSHOT: фиксируем данные на момент заказа ===
    product_title = models.CharField(
        max_length=200,
        verbose_name='Название товара',
    )
    unit_price = models.PositiveIntegerField(
        verbose_name='Цена за единицу (копейки)',
    )
    line_total = models.PositiveIntegerField(
        verbose_name='Сумма позиции (копейки)',
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='URL фото',
        help_text='Snapshot фото на момент заказа',
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f"{self.product_title} x{self.qty}"

    def save(self, *args, **kwargs):
        # Автоматически считаем line_total
        self.line_total = self.unit_price * self.qty
        super().save(*args, **kwargs)
