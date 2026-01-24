"""User model placeholder."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for Telegram Mini App.

    TODO: Implement full model with Telegram fields.
    """

    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='Telegram ID',
        db_index=True,
    )
    telegram_username = models.CharField(
        max_length=32,
        blank=True,
        verbose_name='Telegram Username',
        db_index=True,
        help_text='Username без @',
    )
    terms_accepted = models.BooleanField(
        default=False,
        verbose_name='Условия приняты',
    )
    terms_accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата принятия условий',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
