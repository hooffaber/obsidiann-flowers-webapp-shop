"""
Conversation state model for storing bot conversation states in DB.
"""
from django.db import models
from asgiref.sync import sync_to_async


class ConversationState(models.Model):
    """
    Store conversation state for users.

    Used instead of in-memory ConversationHandler state for webhook mode.
    """

    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID',
        db_index=True,
    )
    state = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Состояние',
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Данные',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено',
    )

    class Meta:
        verbose_name = 'Состояние разговора'
        verbose_name_plural = 'Состояния разговоров'

    def __str__(self):
        return f"{self.telegram_id}: {self.state}"

    @classmethod
    def get_state(cls, telegram_id: int) -> tuple[str, dict]:
        """Get current state and data for user (sync)."""
        obj, _ = cls.objects.get_or_create(telegram_id=telegram_id)
        return obj.state, obj.data

    @classmethod
    async def aget_state(cls, telegram_id: int) -> tuple[str, dict]:
        """Get current state and data for user (async)."""
        return await sync_to_async(cls.get_state)(telegram_id)

    @classmethod
    def set_state(cls, telegram_id: int, state: str, data: dict = None) -> None:
        """Set state and optionally update data (sync)."""
        obj, _ = cls.objects.get_or_create(telegram_id=telegram_id)
        obj.state = state
        if data is not None:
            obj.data = data
        obj.save()

    @classmethod
    async def aset_state(cls, telegram_id: int, state: str, data: dict = None) -> None:
        """Set state and optionally update data (async)."""
        await sync_to_async(cls.set_state)(telegram_id, state, data)

    @classmethod
    def update_data(cls, telegram_id: int, **kwargs) -> None:
        """Update data fields (sync)."""
        obj, _ = cls.objects.get_or_create(telegram_id=telegram_id)
        obj.data.update(kwargs)
        obj.save()

    @classmethod
    async def aupdate_data(cls, telegram_id: int, **kwargs) -> None:
        """Update data fields (async)."""
        await sync_to_async(cls.update_data)(telegram_id, **kwargs)

    @classmethod
    def clear(cls, telegram_id: int) -> None:
        """Clear state and data (sync)."""
        cls.objects.filter(telegram_id=telegram_id).update(state='', data={})

    @classmethod
    async def aclear(cls, telegram_id: int) -> None:
        """Clear state and data (async)."""
        await sync_to_async(cls.clear)(telegram_id)
