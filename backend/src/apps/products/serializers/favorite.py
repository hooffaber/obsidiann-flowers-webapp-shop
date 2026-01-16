"""Favorite serializers."""
from rest_framework import serializers

from apps.products.models import FavoriteAction, Product
from apps.products.serializers.product import ProductListSerializer


class FavoriteActionSerializer(serializers.ModelSerializer):
    """Сериализатор действия с избранным (для истории)."""
    product = ProductListSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = FavoriteAction
        fields = ['id', 'product', 'action', 'action_display', 'created_at']
        read_only_fields = ['id', 'created_at']


class FavoriteToggleSerializer(serializers.Serializer):
    """Сериализатор для добавления/удаления из избранного."""
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Товар не найден')
        return value

    def get_product(self):
        return Product.objects.get(id=self.validated_data['product_id'])


class FavoriteStatusSerializer(serializers.Serializer):
    """Сериализатор для проверки статуса избранного."""
    product_id = serializers.IntegerField()
    is_favorite = serializers.BooleanField()


class FavoriteBulkSerializer(serializers.Serializer):
    """Сериализатор для массовой синхронизации избранного."""
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )

    def validate_product_ids(self, value):
        # Проверяем что все товары существуют
        existing_ids = set(
            Product.objects.filter(
                id__in=value,
                is_active=True,
            ).values_list('id', flat=True)
        )
        invalid_ids = set(value) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f'Товары не найдены: {list(invalid_ids)}'
            )
        return value
