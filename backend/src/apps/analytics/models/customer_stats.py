"""Customer statistics proxy model for admin."""
from django.conf import settings
from django.db import models

from apps.users.models import User


class CustomerStats(User):
    """
    Proxy model for displaying customer statistics in admin.

    Shows aggregated analytics data per customer:
    - Last activity timestamp
    - Order history summary
    - Click history
    - Total purchase value
    """

    class Meta:
        proxy = True
        verbose_name = 'Статистика клиента'
        verbose_name_plural = 'По клиенту'
