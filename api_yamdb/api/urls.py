from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet
)

router = DefaultRouter()
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'genre', GenreViewSet, basename='genre')
router.register(r'title', TitleViewSet, basename='title')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<reviews_id>\d+)/comments/',
    CommentViewSet, basename='comments'
)
app_name = 'api'
urlpatterns = [
    path('v1/', include(router.urls)),
]
