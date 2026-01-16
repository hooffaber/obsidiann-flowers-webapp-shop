"""Products tasks."""
from apps.products.tasks.cleanup import cleanup_old_favorite_actions

__all__ = [
    'cleanup_old_favorite_actions',
]
