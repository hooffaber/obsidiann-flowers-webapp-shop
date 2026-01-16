"""Analytics URLs."""
from django.urls import path

from apps.analytics.views import BatchTrackEventView, TrackEventView

app_name = 'analytics'

urlpatterns = [
    path('track/', TrackEventView.as_view(), name='track'),
    path('track/batch/', BatchTrackEventView.as_view(), name='track-batch'),
]
