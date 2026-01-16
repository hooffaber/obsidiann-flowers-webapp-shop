"""Favorite action model for tracking user favorites history."""
from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class FavoriteActionType(models.TextChoices):
    """Типы действий с избранным."""
    ADDED = 'added', 'Добавлено'
    REMOVED = 'removed', 'Удалено'


class FavoriteAction(TimeStampedModel):
    """
    История действий с избранным.

    Каждое добавление/удаление товара из избранного логируется.
    Позволяет:
    - Отслеживать историю действий пользователя
    - Анализировать популярность товаров
    - Восстанавливать текущее состояние избранного
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_actions',
        verbose_name='Пользователь',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='favorite_actions',
        verbose_name='Товар',
    )
    action = models.CharField(
        max_length=10,
        choices=FavoriteActionType.choices,
        verbose_name='Действие',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Действие с избранным'
        verbose_name_plural = 'История избранного'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user', 'product', '-created_at']),
        ]

    def __str__(self):
        action_label = 'добавил' if self.action == FavoriteActionType.ADDED else 'удалил'
        return f'{self.user} {action_label} "{self.product}" в избранное'

    @classmethod
    def get_user_favorites(cls, user) -> models.QuerySet:
        """
        Получить текущее избранное пользователя.

        Возвращает товары, для которых последнее действие = ADDED.
        """
        from apps.products.models import Product

        # Подзапрос для получения последнего действия по каждому товару
        latest_actions = cls.objects.filter(
            user=user
        ).values('product').annotate(
            latest_id=models.Max('id')
        ).values('latest_id')

        # Получаем ID товаров, где последнее действие = added
        favorite_product_ids = cls.objects.filter(
            id__in=models.Subquery(latest_actions),
            action=FavoriteActionType.ADDED,
        ).values_list('product_id', flat=True)

        return Product.objects.filter(
            id__in=favorite_product_ids,
            is_active=True,
        )

    @classmethod
    def add_to_favorites(cls, user, product) -> 'FavoriteAction':
        """Добавить товар в избранное."""
        return cls.objects.create(
            user=user,
            product=product,
            action=FavoriteActionType.ADDED,
        )

    @classmethod
    def remove_from_favorites(cls, user, product) -> 'FavoriteAction':
        """Удалить товар из избранного."""
        return cls.objects.create(
            user=user,
            product=product,
            action=FavoriteActionType.REMOVED,
        )

    @classmethod
    def is_favorite(cls, user, product) -> bool:
        """Проверить, находится ли товар в избранном."""
        last_action = cls.objects.filter(
            user=user,
            product=product,
        ).order_by('-created_at').first()

        return last_action is not None and last_action.action == FavoriteActionType.ADDED
