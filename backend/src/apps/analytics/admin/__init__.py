"""Analytics admin with Unfold."""
from django.contrib import admin
from django.db.models import Count, Sum, Q, Max, F
from django.db.models.functions import TruncDate, Coalesce
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from datetime import timedelta
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import display

from apps.analytics.models import AnalyticsEvent, DailyStats, EventType, CustomerStats


@admin.register(DailyStats)
class DailyStatsAdmin(ModelAdmin):
    """Админка дневной статистики - По приложению."""

    list_display = [
        'date',
        'show_new_users',
        'show_active_users',
        'show_product_clicks',
        'show_cart_activity',
        'show_searches',
        'show_orders',
        'show_revenue',
    ]
    list_filter = [
        ('date', RangeDateFilter),
    ]
    ordering = ['-date']
    list_per_page = 31  # Месяц
    date_hierarchy = 'date'
    readonly_fields = [
        'date', 'new_users', 'active_users', 'total_events',
        'product_views', 'product_clicks', 'cart_adds', 'cart_removes',
        'searches', 'orders', 'revenue', 'updated_at',
        'show_top_products', 'show_top_searches', 'show_top_categories',
        'show_cart_products',
    ]

    fieldsets = (
        ('Основные показатели', {
            'fields': (
                'date',
                ('new_users', 'active_users'),
                ('orders', 'revenue'),
            ),
        }),
        ('Товары', {
            'fields': (
                ('product_views', 'product_clicks'),
                'show_top_products',
            ),
        }),
        ('Корзина', {
            'fields': (
                ('cart_adds', 'cart_removes'),
                'show_cart_products',
            ),
        }),
        ('Поиск', {
            'fields': (
                'searches',
                'show_top_searches',
            ),
        }),
        ('Категории', {
            'fields': (
                'show_top_categories',
            ),
        }),
    )

    # Запрещаем создание/редактирование (только просмотр)
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True  # Allow viewing change form

    def has_delete_permission(self, request, obj=None):
        return False

    @display(description='Новых')
    def show_new_users(self, obj):
        if obj.new_users > 0:
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">+{}</span>',
                obj.new_users
            )
        return '0'

    @display(description='DAU')
    def show_active_users(self, obj):
        return format_html(
            '<span style="font-weight: 600;">{}</span>',
            obj.active_users
        )

    @display(description='Клики')
    def show_product_clicks(self, obj):
        return obj.product_clicks

    @display(description='Корзина +/-')
    def show_cart_activity(self, obj):
        return format_html(
            '<span style="color: #10b981;">+{}</span> / '
            '<span style="color: #ef4444;">-{}</span>',
            obj.cart_adds, obj.cart_removes
        )

    @display(description='Поиски')
    def show_searches(self, obj):
        return obj.searches if obj.searches > 0 else '—'

    @display(description='Заказов')
    def show_orders(self, obj):
        if obj.orders > 0:
            return format_html(
                '<span style="color: #8b5cf6; font-weight: 600;">{}</span>',
                obj.orders
            )
        return '0'

    @display(description='Выручка')
    def show_revenue(self, obj):
        if obj.revenue > 0:
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">{}</span>',
                obj.revenue_display
            )
        return '—'

    @display(description='Топ товаров по кликам')
    def show_top_products(self, obj):
        """Показывает топ-10 товаров по кликам за день."""
        top_products = AnalyticsEvent.objects.filter(
            event_date=obj.date,
            event_type__in=[EventType.PRODUCT_CLICK, EventType.PRODUCT_VIEW],
            product__isnull=False
        ).values(
            'product__id', 'product__title', 'product__slug'
        ).annotate(
            clicks=Count('id', filter=Q(event_type=EventType.PRODUCT_CLICK)),
            views=Count('id', filter=Q(event_type=EventType.PRODUCT_VIEW)),
        ).order_by('-clicks', '-views')[:10]

        if not top_products:
            return format_html('<span style="color: #9ca3af;">Нет данных</span>')

        rows = []
        for p in top_products:
            url = reverse('admin:products_product_change', args=[p['product__id']])
            rows.append(
                f'<tr>'
                f'<td><a href="{url}" style="color: #6366f1;">{p["product__title"][:40]}</a></td>'
                f'<td style="text-align: right;">{p["clicks"]}</td>'
                f'<td style="text-align: right;">{p["views"]}</td>'
                f'</tr>'
            )

        return format_html(
            '<table style="width: 100%; border-collapse: collapse;">'
            '<thead><tr style="background: #f9fafb;">'
            '<th style="text-align: left; padding: 8px;">Товар</th>'
            '<th style="text-align: right; padding: 8px;">Клики</th>'
            '<th style="text-align: right; padding: 8px;">Просмотры</th>'
            '</tr></thead>'
            '<tbody>{}</tbody>'
            '</table>',
            format_html(''.join(rows))
        )

    @display(description='Топ поисковых запросов')
    def show_top_searches(self, obj):
        """Показывает топ-10 поисковых запросов за день."""
        top_searches = AnalyticsEvent.objects.filter(
            event_date=obj.date,
            event_type=EventType.SEARCH,
            search_query__gt=''
        ).values('search_query').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        if not top_searches:
            return format_html('<span style="color: #9ca3af;">Нет данных</span>')

        rows = []
        for s in top_searches:
            rows.append(
                f'<tr>'
                f'<td><code style="background: #f3f4f6; padding: 2px 6px; border-radius: 4px;">'
                f'{s["search_query"][:50]}</code></td>'
                f'<td style="text-align: right;">{s["count"]}</td>'
                f'</tr>'
            )

        return format_html(
            '<table style="width: 100%; border-collapse: collapse;">'
            '<thead><tr style="background: #f9fafb;">'
            '<th style="text-align: left; padding: 8px;">Запрос</th>'
            '<th style="text-align: right; padding: 8px;">Кол-во</th>'
            '</tr></thead>'
            '<tbody>{}</tbody>'
            '</table>',
            format_html(''.join(rows))
        )

    @display(description='Топ категорий')
    def show_top_categories(self, obj):
        """Показывает топ категорий по кликам за день."""
        top_categories = AnalyticsEvent.objects.filter(
            event_date=obj.date,
            event_type=EventType.CATEGORY_VIEW,
            category__isnull=False
        ).values(
            'category__id', 'category__title'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        if not top_categories:
            return format_html('<span style="color: #9ca3af;">Нет данных</span>')

        rows = []
        for c in top_categories:
            url = reverse('admin:products_category_change', args=[c['category__id']])
            rows.append(
                f'<tr>'
                f'<td><a href="{url}" style="color: #8b5cf6;">{c["category__title"]}</a></td>'
                f'<td style="text-align: right;">{c["count"]}</td>'
                f'</tr>'
            )

        return format_html(
            '<table style="width: 100%; border-collapse: collapse;">'
            '<thead><tr style="background: #f9fafb;">'
            '<th style="text-align: left; padding: 8px;">Категория</th>'
            '<th style="text-align: right; padding: 8px;">Переходы</th>'
            '</tr></thead>'
            '<tbody>{}</tbody>'
            '</table>',
            format_html(''.join(rows))
        )

    @display(description='Активность корзины по товарам')
    def show_cart_products(self, obj):
        """Показывает товары с активностью в корзине."""
        cart_activity = AnalyticsEvent.objects.filter(
            event_date=obj.date,
            event_type__in=[EventType.CART_ADD, EventType.CART_REMOVE],
            product__isnull=False
        ).values(
            'product__id', 'product__title'
        ).annotate(
            adds=Count('id', filter=Q(event_type=EventType.CART_ADD)),
            removes=Count('id', filter=Q(event_type=EventType.CART_REMOVE)),
        ).order_by('-adds')[:10]

        if not cart_activity:
            return format_html('<span style="color: #9ca3af;">Нет данных</span>')

        rows = []
        for p in cart_activity:
            url = reverse('admin:products_product_change', args=[p['product__id']])
            rows.append(
                f'<tr>'
                f'<td><a href="{url}" style="color: #6366f1;">{p["product__title"][:40]}</a></td>'
                f'<td style="text-align: right; color: #10b981;">+{p["adds"]}</td>'
                f'<td style="text-align: right; color: #ef4444;">-{p["removes"]}</td>'
                f'</tr>'
            )

        return format_html(
            '<table style="width: 100%; border-collapse: collapse;">'
            '<thead><tr style="background: #f9fafb;">'
            '<th style="text-align: left; padding: 8px;">Товар</th>'
            '<th style="text-align: right; padding: 8px;">Добавили</th>'
            '<th style="text-align: right; padding: 8px;">Удалили</th>'
            '</tr></thead>'
            '<tbody>{}</tbody>'
            '</table>',
            format_html(''.join(rows))
        )


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(ModelAdmin):
    """Админка событий аналитики - детальный просмотр."""

    list_display = [
        'created_at',
        'show_user',
        'show_event_type',
        'show_target',
        'show_search',
    ]
    list_filter = [
        'event_type',
        ('event_date', RangeDateFilter),
        'product__category',
    ]
    search_fields = [
        'user__username',
        'user__first_name',
        'product__title',
        'search_query',
    ]
    ordering = ['-created_at']
    list_per_page = 50
    date_hierarchy = 'event_date'

    # Запрещаем создание/редактирование
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'product', 'category'
        )

    @display(description='Пользователь')
    def show_user(self, obj):
        if obj.user:
            username = obj.user.username
            if username and not username.startswith('telegram_user_'):
                return format_html(
                    '<a href="https://t.me/{}" target="_blank" '
                    'style="color: #0ea5e9; text-decoration: none;">@{}</a>',
                    username, username
                )
            return format_html(
                '<span style="color: #6b7280;">ID: {}</span>',
                obj.user.telegram_id or obj.user.id
            )
        return format_html(
            '<span style="color: #9ca3af;">Аноним</span>'
        )

    @display(description='Событие')
    def show_event_type(self, obj):
        icons = {
            EventType.APP_OPEN: '📱',
            EventType.PRODUCT_VIEW: '👀',
            EventType.PRODUCT_CLICK: '👆',
            EventType.CART_ADD: '🛒',
            EventType.CART_REMOVE: '❌',
            EventType.CATEGORY_VIEW: '📂',
            EventType.SEARCH: '🔍',
            EventType.CHECKOUT_START: '💳',
            EventType.ORDER_COMPLETE: '✅',
        }
        icon = icons.get(obj.event_type, '•')
        return f'{icon} {obj.get_event_type_display()}'

    @display(description='Объект')
    def show_target(self, obj):
        if obj.product:
            return format_html(
                '<span style="color: #6366f1;">{}</span>',
                obj.product.title[:40] + ('...' if len(obj.product.title) > 40 else '')
            )
        if obj.category:
            return format_html(
                '<span style="color: #8b5cf6;">{}</span>',
                obj.category.title
            )
        return '—'

    @display(description='Запрос')
    def show_search(self, obj):
        if obj.search_query:
            return format_html(
                '<code style="background: #f3f4f6; padding: 2px 6px; border-radius: 4px;">{}</code>',
                obj.search_query[:30] + ('...' if len(obj.search_query) > 30 else '')
            )
        return '—'


@admin.register(CustomerStats)
class CustomerStatsAdmin(ModelAdmin):
    """Админка статистики по клиентам - По клиенту."""

    list_display = [
        'show_avatar',
        'show_telegram',
        'show_last_activity',
        'show_orders_summary',
        'show_total_spent',
        'show_activity_summary',
        'show_actions',
    ]
    list_display_links = ['show_avatar', 'show_telegram']
    list_filter = [
        'is_active',
        ('date_joined', RangeDateFilter),
    ]
    search_fields = ['username', 'first_name', 'last_name', 'telegram_id']
    ordering = ['-date_joined']
    list_per_page = 25

    # Read-only admin - no add/change/delete
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Exclude staff users - only show customers
        qs = qs.filter(is_staff=False)
        # Annotate with aggregated data
        qs = qs.annotate(
            _orders_count=Count('orders', distinct=True),
            _total_spent=Sum('orders__total'),
            _last_activity=Max('analytics_events__created_at'),
            _product_views=Count(
                'analytics_events',
                filter=Q(analytics_events__event_type=EventType.PRODUCT_VIEW),
            ),
            _product_clicks=Count(
                'analytics_events',
                filter=Q(analytics_events__event_type=EventType.PRODUCT_CLICK),
            ),
            _cart_adds=Count(
                'analytics_events',
                filter=Q(analytics_events__event_type=EventType.CART_ADD),
            ),
            _searches=Count(
                'analytics_events',
                filter=Q(analytics_events__event_type=EventType.SEARCH),
            ),
        )
        return qs

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
        if obj.username and not obj.username.startswith('telegram_user_'):
            return format_html(
                '<a href="https://t.me/{}" target="_blank" style="color: #0369a1; text-decoration: none;">'
                '@{}</a>',
                obj.username, obj.username
            )
        if obj.telegram_id:
            return format_html(
                '<span style="font-family: monospace; color: #6b7280;">ID: {}</span>',
                obj.telegram_id
            )
        return '—'

    @display(description='Последняя активность')
    def show_last_activity(self, obj):
        last_activity = getattr(obj, '_last_activity', None)
        if last_activity:
            now = timezone.now()
            diff = now - last_activity

            if diff.days == 0:
                hours = diff.seconds // 3600
                if hours == 0:
                    minutes = diff.seconds // 60
                    time_str = f'{minutes} мин. назад' if minutes > 0 else 'только что'
                else:
                    time_str = f'{hours} ч. назад'
                color = '#10b981'  # Green for today
            elif diff.days == 1:
                time_str = 'вчера'
                color = '#f59e0b'  # Yellow for yesterday
            elif diff.days < 7:
                time_str = f'{diff.days} дн. назад'
                color = '#f59e0b'
            elif diff.days < 30:
                weeks = diff.days // 7
                time_str = f'{weeks} нед. назад'
                color = '#6b7280'  # Gray for older
            else:
                time_str = last_activity.strftime('%d.%m.%Y')
                color = '#9ca3af'

            return format_html(
                '<span style="color: {};">{}</span>',
                color, time_str
            )
        return format_html('<span style="color: #9ca3af;">—</span>')

    @display(description='Заказы')
    def show_orders_summary(self, obj):
        orders_count = getattr(obj, '_orders_count', 0)
        if orders_count > 0:
            # Get order statuses breakdown
            from apps.orders.models import OrderStatus
            done_count = obj.orders.filter(status=OrderStatus.DONE).count()
            cancelled_count = obj.orders.filter(status=OrderStatus.CANCELLED).count()
            active_count = orders_count - done_count - cancelled_count

            parts = []
            if done_count > 0:
                parts.append(f'<span style="color: #10b981;">✓{done_count}</span>')
            if active_count > 0:
                parts.append(f'<span style="color: #3b82f6;">⋯{active_count}</span>')
            if cancelled_count > 0:
                parts.append(f'<span style="color: #ef4444;">✗{cancelled_count}</span>')

            return format_html(
                '<div style="font-weight: 600;">{}</div>'
                '<div style="font-size: 11px;">{}</div>',
                orders_count,
                format_html(' '.join(parts)) if parts else ''
            )
        return format_html('<span style="color: #9ca3af;">0</span>')

    @display(description='Потрачено')
    def show_total_spent(self, obj):
        total = getattr(obj, '_total_spent', None)
        if total:
            formatted = f"{total // 100:,}".replace(',', ' ') + ' ₽'
            return format_html(
                '<strong style="color: #10b981;">{}</strong>',
                formatted
            )
        return format_html('<span style="color: #9ca3af;">0 ₽</span>')

    @display(description='Активность')
    def show_activity_summary(self, obj):
        views = getattr(obj, '_product_views', 0)
        clicks = getattr(obj, '_product_clicks', 0)
        cart_adds = getattr(obj, '_cart_adds', 0)
        searches = getattr(obj, '_searches', 0)

        parts = []
        if views > 0:
            parts.append(f'<span title="Просмотры">👀 {views}</span>')
        if clicks > 0:
            parts.append(f'<span title="Клики">👆 {clicks}</span>')
        if cart_adds > 0:
            parts.append(f'<span title="В корзину">🛒 {cart_adds}</span>')
        if searches > 0:
            parts.append(f'<span title="Поиски">🔍 {searches}</span>')

        if parts:
            return format_html(
                '<div style="display: flex; gap: 8px; font-size: 12px;">{}</div>',
                format_html(' '.join(parts))
            )
        return format_html('<span style="color: #9ca3af;">—</span>')

    @display(description='')
    def show_actions(self, obj):
        # Link to filter analytics events by this user
        events_url = reverse('admin:analytics_analyticsevent_changelist')
        events_url += f'?user__id__exact={obj.id}'

        # Link to user's orders
        orders_url = reverse('admin:orders_order_changelist')
        orders_url += f'?user__id__exact={obj.id}'

        return format_html(
            '<div style="display: flex; gap: 4px;">'
            '<a href="{}" title="История событий" '
            'style="padding: 4px 8px; background: #f3f4f6; border-radius: 4px; text-decoration: none;">📊</a>'
            '<a href="{}" title="Заказы" '
            'style="padding: 4px 8px; background: #f3f4f6; border-radius: 4px; text-decoration: none;">📦</a>'
            '</div>',
            events_url, orders_url
        )
