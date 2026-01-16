"""Core views."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import PageContent
from apps.core.serializers import PageContentSerializer


class PageContentView(APIView):
    """Получение контента страницы по slug."""

    def get(self, request, slug: str):
        try:
            page = PageContent.objects.get(slug=slug, is_active=True)
        except PageContent.DoesNotExist:
            return Response(
                {'detail': 'Страница не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PageContentSerializer(page)
        return Response(serializer.data)
