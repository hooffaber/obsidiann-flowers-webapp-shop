"""Order views."""
import logging

from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.orders.models import Order
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Заказы пользователя.

    list: Список заказов текущего пользователя
    retrieve: Детали заказа
    create: Оформление заказа
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .annotate(items_count=Count('items'))
            .prefetch_related('items')
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        logger.info(
            "Order created: id=%s user=%s total=%s items=%d",
            order.id,
            request.user.id,
            order.total,
            order.items.count(),
        )

        # Возвращаем созданный заказ
        output_serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
