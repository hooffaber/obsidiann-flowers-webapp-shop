"""Base DAO class."""
from typing import Generic, TypeVar

from django.db import models

T = TypeVar('T', bound=models.Model)


class BaseDAO(Generic[T]):
    """
    Base Data Access Object.

    Provides common database operations for models.
    All database queries should go through DAO layer.
    """

    model: type[T]

    def get_by_id(self, id: str) -> T | None:
        raise NotImplementedError

    def get_all(self) -> models.QuerySet[T]:
        raise NotImplementedError

    def create(self, **kwargs) -> T:
        raise NotImplementedError

    def update(self, instance: T, **kwargs) -> T:
        raise NotImplementedError

    def delete(self, instance: T) -> None:
        raise NotImplementedError
