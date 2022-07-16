from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import get_token, send_confirmation_code, UserViewSet


v1_router = DefaultRouter()
v1_router.register('users', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', send_confirmation_code),
    path('v1/auth/token/', get_token),
    path('v1/', include(v1_router.urls))
]
