"""
Bot admin model for managing Telegram bot administrators.
"""
from django.db import models
from django.conf import settings
from asgiref.sync import sync_to_async


class BotAdmin(models.Model):
    """
    Telegram bot administrator.

    Users with this record can use admin commands like /broadcast.
    Add admin by username (with @), telegram_id fills automatically on first use.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bot_admin',
        verbose_name='Пользователь',
        help_text='Связанный пользователь (опционально)',
    )
    username = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Username',
        help_text='Username в Telegram (например @username)',
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='Telegram ID',
        help_text='Заполняется автоматически при первом использовании',
    )
    first_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Имя',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
        help_text='Может ли использовать админ-команды',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлен',
    )
    note = models.TextField(
        blank=True,
        verbose_name='Заметка',
        help_text='Любая заметка об этом админе',
    )

    class Meta:
        verbose_name = 'Админ бота'
        verbose_name_plural = 'Админы бота'
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Ensure username starts with @
        if self.username and not self.username.startswith('@'):
            self.username = f'@{self.username}'
        super().save(*args, **kwargs)

    @classmethod
    def is_admin(cls, telegram_id: int = None, username: str = None) -> bool:
        """
        Check if user is an active admin.

        Checks by telegram_id first, then by username.
        """
        if telegram_id:
            if cls.objects.filter(telegram_id=telegram_id, is_active=True).exists():
                return True

        if username:
            # Normalize username
            if not username.startswith('@'):
                username = f'@{username}'
            return cls.objects.filter(username__iexact=username, is_active=True).exists()

        return False

    @classmethod
    def get_and_update(cls, telegram_id: int, username: str = None) -> 'BotAdmin | None':
        """
        Get admin and update telegram_id if needed (sync version).

        Called when admin uses a command - fills telegram_id if it was empty.
        """
        admin = None

        # Try by telegram_id first
        if telegram_id:
            admin = cls.objects.filter(telegram_id=telegram_id, is_active=True).first()

        # Try by username if not found
        if not admin and username:
            if not username.startswith('@'):
                username = f'@{username}'
            admin = cls.objects.filter(username__iexact=username, is_active=True).first()

            # Update telegram_id if found by username
            if admin and not admin.telegram_id:
                admin.telegram_id = telegram_id
                admin.save(update_fields=['telegram_id'])

        return admin

    @classmethod
    async def aget_and_update(cls, telegram_id: int, username: str = None) -> 'BotAdmin | None':
        """
        Get admin and update telegram_id if needed (async version).

        Called when admin uses a command - fills telegram_id if it was empty.
        """
        return await sync_to_async(cls.get_and_update)(telegram_id, username)
