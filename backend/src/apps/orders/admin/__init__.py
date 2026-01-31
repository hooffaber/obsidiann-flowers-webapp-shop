"""Orders admin with Unfold."""
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RangeDateFilter, DropdownFilter
from unfold.decorators import display

from apps.orders.models import Order, OrderItem, OrderStatus, PaymentMethod


class StatusFilter(DropdownFilter):
    title = 'Статус'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return OrderStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class OrderItemInline(TabularInline):
    """Позиции заказа."""
    model = OrderItem
    extra = 0
    readonly_fields = [
        'show_image',
        'product_title',
        'qty',
        'show_unit_price',
        'show_line_total',
    ]
    fields = ['show_image', 'product_title', 'qty', 'show_unit_price', 'show_line_total']
    can_delete = False
    max_num = 0
    tab = True

    @display(description='')
    def show_image(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 6px; object-fit: cover;" />',
                obj.image_url
            )
        return '—'

    @display(description='Цена')
    def show_unit_price(self, obj):
        if obj.unit_price is None:
            return '—'
        return f"{obj.unit_price // 100:,}".replace(',', ' ') + ' ₽'

    @display(description='Сумма')
    def show_line_total(self, obj):
        if obj.line_total is None:
            return '—'
        return format_html(
            '<strong>{}</strong>',
            f"{obj.line_total // 100:,}".replace(',', ' ') + ' ₽'
        )


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    """Админка заказов."""
    list_display = [
        'show_id',
        'show_status',
        'customer_name',
        'customer_phone',
        'show_total',
        'show_items_count',
        'show_created',
    ]
    list_display_links = ['show_id', 'customer_name']
    list_filter = [
        StatusFilter,
        ('created_at', RangeDateFilter),
    ]
    search_fields = ['uid', 'customer_name', 'customer_phone', 'delivery_address']
    readonly_fields = [
        'user',
        'show_subtotal',
        'show_delivery_fee',
        'show_discount',
        'show_total_detail',
        'created_at',
        'updated_at',
    ]
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Статус заказа', {
            'fields': ('status', 'payment_method'),
            'classes': ['tab'],
        }),
        ('Клиент', {
            'fields': ('user', 'customer_name', 'customer_phone'),
            'classes': ['tab'],
        }),
        ('Доставка', {
            'fields': (
                'delivery_address',
                'delivery_comment',
                'delivery_date',
                ('delivery_time_from', 'delivery_time_to'),
            ),
            'classes': ['tab'],
        }),
        ('Суммы', {
            'fields': (
                'show_subtotal',
                ('delivery_fee', 'show_delivery_fee'),
                ('discount', 'show_discount'),
                'show_total_detail',
            ),
            'classes': ['tab'],
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['tab', 'collapse'],
        }),
    )

    @display(description='№')
    def show_id(self, obj):
        return format_html(
            '<span style="font-family: monospace; font-weight: 600;">#{}</span>',
            obj.uid
        )

    @display(description='Статус')
    def show_status(self, obj):
        colors = {
            'new': ('#3b82f6', '#eff6ff'),
            'confirmed': ('#8b5cf6', '#f5f3ff'),
            'in_progress': ('#f59e0b', '#fffbeb'),
            'delivering': ('#06b6d4', '#ecfeff'),
            'done': ('#10b981', '#ecfdf5'),
            'cancelled': ('#ef4444', '#fef2f2'),
        }
        fg, bg = colors.get(obj.status, ('#6b7280', '#f9fafb'))
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 500;">{}</span>',
            bg, fg, obj.get_status_display()
        )

    @display(description='Сумма')
    def show_total(self, obj):
        if obj.total is None:
            return '—'
        return format_html(
            '<strong style="font-size: 14px;">{}</strong>',
            f"{obj.total // 100:,}".replace(',', ' ') + ' ₽'
        )

    @display(description='Позиций')
    def show_items_count(self, obj):
        count = obj.items.count()
        return count

    @display(description='Создан')
    def show_created(self, obj):
        return format_html(
            '<span style="color: #6b7280; font-size: 13px;">{}</span>',
            obj.created_at.strftime('%d.%m.%Y %H:%M')
        )

    # Detail view displays
    @display(description='Сумма товаров')
    def show_subtotal(self, obj):
        if obj.subtotal is None:
            return '—'
        return format_html(
            '<span style="font-size: 16px;">{}</span>',
            f"{obj.subtotal // 100:,}".replace(',', ' ') + ' ₽'
        )

    @display(description='')
    def show_delivery_fee(self, obj):
        if obj.delivery_fee:
            return f"{obj.delivery_fee // 100:,}".replace(',', ' ') + ' ₽'
        return 'Бесплатно'

    @display(description='')
    def show_discount(self, obj):
        if obj.discount:
            return f"-{obj.discount // 100:,}".replace(',', ' ') + ' ₽'
        return '—'

    @display(description='ИТОГО')
    def show_total_detail(self, obj):
        if obj.total is None:
            return '—'
        return format_html(
            '<span style="font-size: 20px; font-weight: 700; color: #10b981;">{}</span>',
            f"{obj.total // 100:,}".replace(',', ' ') + ' ₽'
        )
