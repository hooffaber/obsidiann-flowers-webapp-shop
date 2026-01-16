"""Core serializers."""
from rest_framework import serializers

from apps.core.models import PageContent


class PageContentSerializer(serializers.ModelSerializer):
    """Сериализатор для контента страниц."""

    class Meta:
        model = PageContent
        fields = ['slug', 'title', 'content']
