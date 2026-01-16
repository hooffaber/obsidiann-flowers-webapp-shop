"""Favorite views."""
from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.products.models import FavoriteAction, FavoriteActionType, Product, ProductImage
from apps.products.serializers import (
    FavoriteActionSerializer,
    FavoriteBulkSerializer,
    FavoriteToggleSerializer,
    ProductListSerializer,
)


class FavoriteViewSet(viewsets.ViewSet):
    """
    Избранное пользователя.

    Endpoints:
    - GET /favorites/ — список товаров в избранном
    - POST /favorites/ — добавить товар в избранное
    - DELETE /favorites/{product_id}/ — удалить товар из избранного
    - GET /favorites/history/ — история действий с избранным
    - POST /favorites/sync/ — синхронизация избранного (для миграции из localStorage)
    - POST /favorites/check/ — проверить статусы товаров
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Получить текущее избранное."""
        products = FavoriteAction.get_user_favorites(request.user)
        products = products.select_related('category').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.order_by('-is_main', 'sort_order')
            )
        )
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Добавить товар в избранное."""
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.get_product()

        # Проверяем, не в избранном ли уже
        if FavoriteAction.is_favorite(request.user, product):
            return Response(
                {'detail': 'Товар уже в избранном'},
                status=status.HTTP_200_OK
            )

        FavoriteAction.add_to_favorites(request.user, product)
        return Response(
            {'detail': 'Добавлено в избранное', 'is_favorite': True},
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, pk=None):
        """Удалить товар из избранного."""
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем, есть ли в избранном
        if not FavoriteAction.is_favorite(request.user, product):
            return Response(
                {'detail': 'Товар не в избранном'},
                status=status.HTTP_200_OK
            )

        FavoriteAction.remove_from_favorites(request.user, product)
        return Response(
            {'detail': 'Удалено из избранного', 'is_favorite': False},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def history(self, request):
        """История действий с избранным."""
        actions = FavoriteAction.objects.filter(
            user=request.user
        ).select_related(
            'product', 'product__category'
        ).prefetch_related(
            Prefetch(
                'product__images',
                queryset=ProductImage.objects.order_by('-is_main', 'sort_order')
            )
        )[:100]  # Лимит 100 последних действий

        serializer = FavoriteActionSerializer(actions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def sync(self, request):
        """
        Синхронизация избранного.

        Используется для миграции из localStorage на сервер.
        Принимает список product_ids, устанавливает их как избранное.
        """
        serializer = FavoriteBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_ids = set(serializer.validated_data['product_ids'])

        # Получаем текущие избранные товары
        current_favorites = set(
            FavoriteAction.get_user_favorites(request.user).values_list('id', flat=True)
        )

        # Добавляем новые
        to_add = product_ids - current_favorites
        for product_id in to_add:
            product = Product.objects.get(id=product_id)
            FavoriteAction.add_to_favorites(request.user, product)

        # Удаляем те, что больше не в списке
        to_remove = current_favorites - product_ids
        for product_id in to_remove:
            product = Product.objects.get(id=product_id)
            FavoriteAction.remove_from_favorites(request.user, product)

        return Response({
            'detail': 'Избранное синхронизировано',
            'added': len(to_add),
            'removed': len(to_remove),
        })

    @action(detail=False, methods=['post'])
    def check(self, request):
        """
        Проверить статусы товаров.

        Принимает список product_ids, возвращает какие из них в избранном.
        """
        serializer = FavoriteBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_ids = serializer.validated_data['product_ids']

        # Получаем текущие избранные
        favorites = set(
            FavoriteAction.get_user_favorites(request.user).values_list('id', flat=True)
        )

        result = [
            {'product_id': pid, 'is_favorite': pid in favorites}
            for pid in product_ids
        ]

        return Response(result)
