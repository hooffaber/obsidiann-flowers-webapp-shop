"""Analytics tasks."""
from apps.analytics.tasks.aggregate import aggregate_daily_stats, cleanup_old_events

__all__ = [
    'aggregate_daily_stats',
    'cleanup_old_events',
]
