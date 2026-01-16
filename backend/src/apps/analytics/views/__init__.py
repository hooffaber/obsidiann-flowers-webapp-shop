"""Analytics views."""
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.models import AnalyticsEvent
from apps.analytics.serializers import BatchTrackEventSerializer, TrackEventSerializer
from apps.products.models import Category, Product


class TrackEventView(APIView):
    """
    Трекинг событий аналитики.

    POST /api/v1/analytics/track/
    """

    permission_classes = [AllowAny]  # Разрешаем анонимные события

    def post(self, request):
        serializer = TrackEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = request.user if request.user.is_authenticated else None

        # Получаем связанные объекты
        product = None
        category = None

        if data.get('product_id'):
            try:
                product = Product.objects.get(id=data['product_id'])
            except Product.DoesNotExist:
                pass

        if data.get('category_id'):
            try:
                category = Category.objects.get(id=data['category_id'])
            except Category.DoesNotExist:
                pass

        # Создаём событие
        AnalyticsEvent.objects.create(
            user=user,
            event_type=data['event_type'],
            product=product,
            category=category,
            search_query=data.get('search_query', ''),
            metadata=data.get('metadata', {}),
            session_id=data.get('session_id', ''),
            event_date=timezone.now().date(),
        )

        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)


class BatchTrackEventView(APIView):
    """
    Пакетный трекинг событий.

    POST /api/v1/analytics/track/batch/
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = BatchTrackEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user if request.user.is_authenticated else None
        today = timezone.now().date()

        events_to_create = []
        for event_data in serializer.validated_data['events']:
            product = None
            category = None

            if event_data.get('product_id'):
                try:
                    product = Product.objects.get(id=event_data['product_id'])
                except Product.DoesNotExist:
                    pass

            if event_data.get('category_id'):
                try:
                    category = Category.objects.get(id=event_data['category_id'])
                except Category.DoesNotExist:
                    pass

            events_to_create.append(AnalyticsEvent(
                user=user,
                event_type=event_data['event_type'],
                product=product,
                category=category,
                search_query=event_data.get('search_query', ''),
                metadata=event_data.get('metadata', {}),
                session_id=event_data.get('session_id', ''),
                event_date=today,
            ))

        AnalyticsEvent.objects.bulk_create(events_to_create)

        return Response(
            {'status': 'ok', 'count': len(events_to_create)},
            status=status.HTTP_201_CREATED
        )
