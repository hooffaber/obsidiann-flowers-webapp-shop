from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    'SITE_TITLE': 'Obsidiann Admin',
    'SITE_HEADER': 'Obsidiann Admin',
    # 'SITE_SYMBOL': 'local_florist',  # Закомментировано - используем только текст
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': True,
    'ENVIRONMENT': 'settings.environment.environment_callback',
    'COLORS': {
        'primary': {
            '50': '#fdf2f8',
            '100': '#fce7f3',
            '200': '#fbcfe8',
            '300': '#f9a8d4',
            '400': '#f472b6',
            '500': '#ec4899',
            '600': '#db2777',
            '700': '#be185d',
            '800': '#9d174d',
            '900': '#831843',
            '950': '#500724',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': True,
        'navigation': [
            {
                'title': 'Навигация',
                'separator': True,
                'items': [
                    {
                        'title': 'Дашборд',
                        'icon': 'dashboard',
                        'link': reverse_lazy('admin:index'),
                    },
                ],
            },
            {
                'title': 'Каталог',
                'separator': True,
                'items': [
                    {
                        'title': 'Товары',
                        'icon': 'local_florist',
                        'link': reverse_lazy('admin:products_product_changelist'),
                    },
                    {
                        'title': 'Категории',
                        'icon': 'category',
                        'link': reverse_lazy('admin:products_category_changelist'),
                    },
                ],
            },
            {
                'title': 'Продажи',
                'separator': True,
                'items': [
                    {
                        'title': 'Заказы',
                        'icon': 'shopping_cart',
                        'link': reverse_lazy('admin:orders_order_changelist'),
                    },
                ],
            },
            {
                'title': 'Пользователи',
                'separator': True,
                'items': [
                    {
                        'title': 'Клиенты',
                        'icon': 'people',
                        'link': reverse_lazy('admin:users_user_changelist'),
                    },
                ],
            },
            {
                'title': 'Статистика',
                'separator': True,
                'items': [
                    {
                        'title': 'По приложению',
                        'icon': 'monitoring',
                        'link': reverse_lazy('admin:analytics_dailystats_changelist'),
                    },
                    {
                        'title': 'По клиенту',
                        'icon': 'person_search',
                        'link': reverse_lazy('admin:analytics_customerstats_changelist'),
                    },
                    {
                        'title': 'События',
                        'icon': 'analytics',
                        'link': reverse_lazy('admin:analytics_analyticsevent_changelist'),
                    },
                    {
                        'title': 'История избранного',
                        'icon': 'favorite',
                        'link': reverse_lazy('admin:products_favoriteaction_changelist'),
                    },
                ],
            },
        ],
    },
}


def environment_callback(request) -> str | None:
    """Return environment name for display in admin."""
    from settings.environment import env

    environment = env('ENVIRONMENT', default='development')
    if environment == 'production':
        return None  # Don't show badge in production
    return environment.upper()
