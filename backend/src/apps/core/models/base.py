"""Base models."""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract model with timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    """Abstract base model with UUID primary key."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True
