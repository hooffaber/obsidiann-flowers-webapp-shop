"""Base DTO classes."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class BaseDTO:
    """
    Base Data Transfer Object.

    DTOs are used for transferring data between layers.
    They are immutable and contain no business logic.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert DTO to dictionary."""
        raise NotImplementedError


@dataclass
class PaginatedDTO:
    """Paginated response DTO."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
