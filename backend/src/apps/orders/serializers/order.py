"""Order serializers."""
from rest_framework import serializers

from apps.orders.models import Order, OrderItem, OrderStatus, PaymentMethod
from apps.products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    """Позиция заказа."""
    unit_price_display = serializers.SerializerMethodField()
    line_total_display = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_id',
            'product_title',
            'qty',
            'unit_price',
            'unit_price_display',
            'line_total',
            'line_total_display',
            'image_url',
        ]

    def get_unit_price_display(self, obj) -> str:
        return f"{obj.unit_price // 100:,}".replace(',', '\xa0') + '\xa0₽'

    def get_line_total_display(self, obj) -> str:
        return f"{obj.line_total // 100:,}".replace(',', '\xa0') + '\xa0₽'


class OrderListSerializer(serializers.ModelSerializer):
    """Заказ для списка."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    total_display = serializers.SerializerMethodField()
    items_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'status_display',
            'payment_method',
            'payment_method_display',
            'total',
            'total_display',
            'items_count',
            'customer_name',
            'created_at',
        ]

    def get_total_display(self, obj) -> str:
        return f"{obj.total // 100:,}".replace(',', '\xa0') + '\xa0₽'


class OrderDetailSerializer(serializers.ModelSerializer):
    """Полная информация о заказе."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    subtotal_display = serializers.SerializerMethodField()
    delivery_fee_display = serializers.SerializerMethodField()
    discount_display = serializers.SerializerMethodField()
    total_display = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'status_display',
            'payment_method',
            'payment_method_display',
            'subtotal',
            'subtotal_display',
            'delivery_fee',
            'delivery_fee_display',
            'discount',
            'discount_display',
            'total',
            'total_display',
            'customer_name',
            'customer_phone',
            'delivery_address',
            'delivery_comment',
            'delivery_date',
            'delivery_time_from',
            'delivery_time_to',
            'items',
            'created_at',
            'updated_at',
        ]

    def get_subtotal_display(self, obj) -> str:
        return f"{obj.subtotal // 100:,}".replace(',', '\xa0') + '\xa0₽'

    def get_delivery_fee_display(self, obj) -> str:
        return f"{obj.delivery_fee // 100:,}".replace(',', '\xa0') + '\xa0₽'

    def get_discount_display(self, obj) -> str:
        return f"{obj.discount // 100:,}".replace(',', '\xa0') + '\xa0₽'

    def get_total_display(self, obj) -> str:
        return f"{obj.total // 100:,}".replace(',', '\xa0') + '\xa0₽'


# === Input Serializers ===

class OrderItemCreateSerializer(serializers.Serializer):
    """Позиция для создания заказа."""
    product_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1, default=1)


class OrderCreateSerializer(serializers.Serializer):
    """Создание заказа."""
    customer_name = serializers.CharField(max_length=120)
    customer_phone = serializers.CharField(max_length=32)
    delivery_address = serializers.CharField(max_length=255)
    delivery_comment = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    delivery_date = serializers.DateField(required=False, allow_null=True)
    delivery_time_from = serializers.TimeField(required=False, allow_null=True)
    delivery_time_to = serializers.TimeField(required=False, allow_null=True)
    payment_method = serializers.ChoiceField(
        choices=PaymentMethod.choices,
        default=PaymentMethod.LINK_AFTER_ORDER,
    )
    items = OrderItemCreateSerializer(many=True, min_length=1)

    def validate_items(self, items):
        """Проверяем что товары существуют и доступны."""
        product_ids = [item['product_id'] for item in items]
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        
        if len(products) != len(product_ids):
            raise serializers.ValidationError('Некоторые товары не найдены или недоступны')
        
        # Проверяем наличие
        products_map = {p.id: p for p in products}
        for item in items:
            product = products_map.get(item['product_id'])
            if product and not product.is_unlimited:
                if product.qty_available < item['qty']:
                    raise serializers.ValidationError(
                        f'Недостаточно товара "{product.title}" в наличии'
                    )
        
        return items

    def create(self, validated_data):
        """Создаём заказ с позициями."""
        user = self.context['request'].user
        items_data = validated_data.pop('items')

        # Получаем товары
        product_ids = [item['product_id'] for item in items_data]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        # Создаём заказ
        order = Order.objects.create(user=user, **validated_data)

        # Создаём позиции со snapshot
        order_items = []
        for item_data in items_data:
            product = products[item_data['product_id']]
            main_image = product.images.filter(is_main=True).first() or product.images.first()

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                qty=item_data['qty'],
                product_title=product.title,
                unit_price=product.price,
                line_total=product.price * item_data['qty'],
                image_url=main_image.image.url if main_image else '',
            )
            order_items.append(order_item)

            # Уменьшаем остаток
            if not product.is_unlimited:
                product.qty_available -= item_data['qty']
                product.save(update_fields=['qty_available'])

        # Пересчитываем итоги
        order.calculate_totals()
        order.save()

        # Отправляем уведомление в Telegram
        self._send_order_notification(user, order, order_items)

        return order

    def _send_order_notification(self, user, order, order_items):
        """Отправить уведомление о заказе в Telegram."""
        from apps.bot.tasks import send_order_notification_task, send_admin_order_notification_task

        # Формируем данные о позициях
        items = [
            {
                'title': item.product_title,
                'qty': item.qty,
                'line_total': item.line_total,
            }
            for item in order_items
        ]

        # Формируем дату/время доставки
        delivery_date = None
        delivery_time = None

        if order.delivery_date:
            delivery_date = order.delivery_date.strftime('%d.%m.%Y')

        if order.delivery_time_from and order.delivery_time_to:
            delivery_time = f"{order.delivery_time_from.strftime('%H:%M')}-{order.delivery_time_to.strftime('%H:%M')}"
        elif order.delivery_time_from:
            delivery_time = f"с {order.delivery_time_from.strftime('%H:%M')}"

        # Уведомление клиенту
        if user.telegram_id:
            send_order_notification_task.delay(
                telegram_id=user.telegram_id,
                order_id=order.id,
                items=items,
                total=order.total,
                delivery_fee=order.delivery_fee,
                delivery_address=order.delivery_address,
                delivery_date=delivery_date,
                delivery_time=delivery_time,
            )

        # Уведомление админам
        send_admin_order_notification_task.delay(
            order_id=order.id,
            items=items,
            total=order.total,
            delivery_fee=order.delivery_fee,
            delivery_address=order.delivery_address,
            customer_name=order.customer_name,
            customer_username=user.telegram_username or None,
            customer_phone=order.customer_phone,
            delivery_date=delivery_date,
            delivery_time=delivery_time,
        )
