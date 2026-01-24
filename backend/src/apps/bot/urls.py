"""
Bot URL configuration.
"""
from django.urls import path

from apps.bot.views import WebhookView


app_name = 'bot'

urlpatterns = [
    path('webhook/', WebhookView.as_view(), name='webhook'),
]
