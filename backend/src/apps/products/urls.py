"""Product URLs."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.products.views import CategoryViewSet, FavoriteViewSet, ProductViewSet

app_name = 'products'

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('favorites', FavoriteViewSet, basename='favorite')
router.register('', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
