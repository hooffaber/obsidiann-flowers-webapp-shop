"""Core URLs."""
from django.urls import path

from apps.core.views import PageContentView

app_name = 'core'

urlpatterns = [
    path('pages/<str:slug>/', PageContentView.as_view(), name='page-content'),
]
