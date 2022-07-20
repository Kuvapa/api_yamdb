from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
    UserViewSet,
    get_token,
    send_confirmation_code,
)

v1_router = DefaultRouter()
v1_router.register(r'categories', CategoryViewSet, basename='category')
v1_router.register(r'genres', GenreViewSet, basename='genre')
v1_router.register(r'titles', TitleViewSet, basename='title')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<reviews_id>\d+)/comments/',
    CommentViewSet, basename='comments'
)
v1_router.register('users', UserViewSet, basename='users')
app_name = 'api'
urlpatterns = [
    path('v1/auth/signup/', send_confirmation_code),
    path('v1/auth/token/', get_token),
    path('v1/', include(v1_router.urls)),
]
