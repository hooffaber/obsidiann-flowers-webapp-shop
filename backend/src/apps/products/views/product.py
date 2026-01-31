"""Product views."""
import logging

from django.db import models
from django.db.models import Prefetch
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.products.models import Product, ProductImage
from apps.products.serializers import ProductDetailSerializer, ProductListSerializer

logger = logging.getLogger(__name__)


class ProductFilter(filters.FilterSet):
    """Фильтры для товаров."""
    category = filters.CharFilter(field_name='category__slug')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    in_stock = filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(
                models.Q(is_unlimited=True) | models.Q(qty_available__gt=0)
            )
        return queryset


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Товары.

    list: Каталог товаров (с фильтрацией по категории)
    retrieve: Детали товара по slug
    """
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'sort_order']
    ordering = ['sort_order', '-created_at']

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related(
                Prefetch(
                    'images',
                    queryset=ProductImage.objects.order_by('-is_main', 'sort_order')
                )
            )
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
