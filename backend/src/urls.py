from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


# Декоратор для проверки прав администратора
def is_staff_user(user):
    return user.is_authenticated and user.is_staff

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),

    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.users.urls')),
        path('products/', include('apps.products.urls')),
        path('cart/', include('apps.cart.urls')),
        path('orders/', include('apps.orders.urls')),
        path('payments/', include('apps.payments.urls')),
        path('analytics/', include('apps.analytics.urls')),
        path('', include('apps.core.urls')),
    ])),

    # Health check
    path('health/', include('health_check.urls')),

    # Telegram Bot webhook
    path('api/bot/', include('apps.bot.urls')),

    # API Documentation (только для администраторов)
    path('api/schema/', user_passes_test(is_staff_user)(SpectacularAPIView.as_view()), name='schema'),
    path('api/docs/', user_passes_test(is_staff_user)(SpectacularSwaggerView.as_view(url_name='schema')), name='swagger-ui'),
    path('api/redoc/', user_passes_test(is_staff_user)(SpectacularRedocView.as_view(url_name='schema')), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
