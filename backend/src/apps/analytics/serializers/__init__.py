"""Analytics serializers."""
from rest_framework import serializers

from apps.analytics.models import AnalyticsEvent, EventType


class TrackEventSerializer(serializers.Serializer):
    """Сериализатор для трекинга событий."""

    event_type = serializers.ChoiceField(choices=EventType.choices)
    product_id = serializers.IntegerField(required=False, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    search_query = serializers.CharField(required=False, allow_blank=True, max_length=255)
    metadata = serializers.JSONField(required=False, default=dict)
    session_id = serializers.CharField(required=False, allow_blank=True, max_length=64)


class BatchTrackEventSerializer(serializers.Serializer):
    """Сериализатор для пакетной отправки событий."""

    events = TrackEventSerializer(many=True)
