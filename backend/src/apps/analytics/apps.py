"""Analytics app configuration."""
from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Analytics app config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
    verbose_name = 'Аналитика'
