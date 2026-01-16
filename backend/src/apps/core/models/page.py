"""Page content models."""
from django.db import models

from apps.core.models.base import TimeStampedModel


class PageContent(TimeStampedModel):
    """
    Контент статических страниц (О нас, Доставка и т.д.)

    Singleton-подобная модель: для каждого slug может быть только одна запись.
    """

    class PageSlug(models.TextChoices):
        ABOUT = 'about', 'О нас'
        DELIVERY = 'delivery', 'Доставка'
        CONTACTS = 'contacts', 'Контакты'

    slug = models.CharField(
        'Идентификатор',
        max_length=50,
        choices=PageSlug.choices,
        unique=True,
        help_text='Уникальный идентификатор страницы'
    )
    title = models.CharField(
        'Заголовок',
        max_length=200,
    )
    content = models.TextField(
        'Содержимое',
        help_text='Поддерживает HTML-разметку'
    )
    is_active = models.BooleanField(
        'Активна',
        default=True,
        help_text='Показывать ли страницу пользователям'
    )

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['slug']

    def __str__(self):
        return self.get_slug_display()
