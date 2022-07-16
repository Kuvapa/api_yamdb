from rest_framework import permissions


class AdminOrReadOnlyPermission(permissions.BasePermission):
    """Права администратора, суперюзера и пользователя на чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.is_superuser
            )
        )
