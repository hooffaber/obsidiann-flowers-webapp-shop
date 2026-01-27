"""Users admin with Unfold."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, Sum
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Админка пользователей."""
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = [
        'show_avatar',
        'show_telegram',
        'show_contact_info',
        'show_orders_count',
        'show_total_spent',
        'show_status',
        'date_joined',
    ]
    list_display_links = ['show_avatar', 'show_telegram']
    list_filter = [
        'is_active',
        'is_staff',
        ('date_joined', RangeDateFilter),
    ]
    search_fields = ['username', 'telegram_username', 'first_name', 'last_name', 'telegram_id']
    ordering = ['-date_joined']
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('username', 'password'),
            'classes': ['tab'],
        }),
        ('Telegram', {
            'fields': ('telegram_id', 'telegram_username'),
            'classes': ['tab'],
        }),
        ('Личные данные', {
            'fields': ('first_name', 'last_name', 'email'),
            'classes': ['tab'],
        }),
        ('Права', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ['tab', 'collapse'],
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined'),
            'classes': ['tab', 'collapse'],
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'telegram_id', 'password1', 'password2'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _orders_count=Count('orders'),
            _total_spent=Sum('orders__total'),
        )

    @display(description='')
    def show_avatar(self, obj):
        initials = (obj.first_name[:1] if obj.first_name else obj.username[:1]).upper()
        colors = ['#ec4899', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']
        color = colors[obj.id % len(colors)]
        return format_html(
            '<div style="width: 36px; height: 36px; border-radius: 50%; background: {}; '
            'display: flex; align-items: center; justify-content: center; color: white; '
            'font-weight: 600; font-size: 14px;">{}</div>',
            color, initials
        )

    @display(description='Telegram')
    def show_telegram(self, obj):
        # Показываем telegram_username как ссылку на Telegram
        if obj.telegram_username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank" style="color: #0369a1; text-decoration: none;">'
                '@{}</a>',
                obj.telegram_username, obj.telegram_username
            )
        # Если username нет — показываем ID
        if obj.telegram_id:
            return format_html(
                '<span style="font-family: monospace; color: #6b7280;">ID: {}</span>',
                obj.telegram_id
            )
        return '—'

    @display(description='Контакт из заказа')
    def show_contact_info(self, obj):
        # Показываем имя и телефон из последнего заказа
        last_order = obj.orders.order_by('-created_at').first()
        if last_order:
            return format_html(
                '<div><strong>{}</strong></div>'
                '<div style="color: #6b7280; font-size: 12px;">{}</div>',
                last_order.customer_name,
                last_order.customer_phone,
            )
        return format_html('<span style="color: #9ca3af;">Нет заказов</span>')

    @display(description='Заказов')
    def show_orders_count(self, obj):
        count = getattr(obj, '_orders_count', 0)
        return count if count else '—'

    @display(description='Потрачено')
    def show_total_spent(self, obj):
        total = getattr(obj, '_total_spent', None)
        if total:
            return format_html(
                '<strong>{}</strong>',
                f"{total // 100:,}".replace(',', ' ') + ' ₽'
            )
        return '—'

    @display(description='Статус', label={True: 'success', False: 'danger'})
    def show_status(self, obj):
        return obj.is_active, 'Активен' if obj.is_active else 'Заблокирован'
