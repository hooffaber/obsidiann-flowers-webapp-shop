"""
Broadcast models for Telegram mass messaging.
"""
from django.db import models
from django.conf import settings


class BroadcastStatus(models.TextChoices):
    """Broadcast status choices."""
    DRAFT = 'draft', 'Черновик'
    PENDING = 'pending', 'Ожидает отправки'
    SENDING = 'sending', 'Отправляется'
    COMPLETED = 'completed', 'Завершена'
    CANCELLED = 'cancelled', 'Отменена'
    FAILED = 'failed', 'Ошибка'


class BroadcastContentType(models.TextChoices):
    """Content type choices."""
    TEXT = 'text', 'Текст'
    PHOTO = 'photo', 'Фото'
    VIDEO = 'video', 'Видео'
    DOCUMENT = 'document', 'Документ'
    VOICE = 'voice', 'Голосовое сообщение'


class Broadcast(models.Model):
    """
    Broadcast message model.

    Stores information about mass messages sent to users.
    """

    # Audience - list of usernames (without @)
    recipients_usernames = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Получатели (usernames)',
        help_text='Список username получателей',
    )

    # Content
    content_type = models.CharField(
        max_length=20,
        choices=BroadcastContentType.choices,
        default=BroadcastContentType.TEXT,
        verbose_name='Тип контента',
    )
    text = models.TextField(
        blank=True,
        verbose_name='Текст сообщения',
        help_text='Текст или подпись к медиа',
    )
    file_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='File ID',
        help_text='Telegram file_id для медиа',
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=BroadcastStatus.choices,
        default=BroadcastStatus.DRAFT,
        verbose_name='Статус',
        db_index=True,
    )

    # Creator
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='broadcasts',
        verbose_name='Создал',
    )
    created_by_telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Telegram ID создателя',
    )

    # Statistics
    total_recipients = models.PositiveIntegerField(
        default=0,
        verbose_name='Всего получателей',
    )
    sent_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Отправлено',
    )
    failed_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Ошибок',
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создана',
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Начата',
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Завершена',
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Рассылка #{self.pk} ({self.get_status_display()})"

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_recipients == 0:
            return 0.0
        return (self.sent_count / self.total_recipients) * 100


class BroadcastLogStatus(models.TextChoices):
    """Log entry status choices."""
    PENDING = 'pending', 'Ожидает'
    SENT = 'sent', 'Отправлено'
    FAILED = 'failed', 'Ошибка'
    BLOCKED = 'blocked', 'Заблокирован'


class BroadcastLog(models.Model):
    """
    Log entry for each broadcast recipient.

    Tracks delivery status for each user.
    """

    broadcast = models.ForeignKey(
        Broadcast,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Рассылка',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='broadcast_logs',
        verbose_name='Пользователь',
    )
    telegram_id = models.BigIntegerField(
        verbose_name='Telegram ID',
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=BroadcastLogStatus.choices,
        default=BroadcastLogStatus.PENDING,
        verbose_name='Статус',
        db_index=True,
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Сообщение об ошибке',
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Отправлено в',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
    )

    class Meta:
        verbose_name = 'Лог рассылки'
        verbose_name_plural = 'Логи рассылок'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['broadcast', 'status']),
        ]

    def __str__(self):
        return f"Log #{self.pk} - {self.get_status_display()}"
