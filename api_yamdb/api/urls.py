from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet

router = DefaultRouter()
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'genre', GenreViewSet, basename='genre')
router.register(r'title', TitleViewSet, basename='title')

app_name = 'api'
urlpatterns = [
    path('v1/', include(router.urls)),
]
