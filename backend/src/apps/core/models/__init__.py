"""Core models."""
from apps.core.models.base import BaseModel, TimeStampedModel
from apps.core.models.page import PageContent

__all__ = [
    'BaseModel',
    'TimeStampedModel',
    'PageContent',
]
