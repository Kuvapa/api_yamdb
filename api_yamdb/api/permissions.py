from rest_framework import permissions


class AdminOnlyPermission(permissions.BasePermission):
    """Права администратора и суперюзера Django."""

    def has_permission(self, request, view):
        if request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'admin'
        ):
            return True


class AdminModeratorAuthorPermission(permissions.BasePermission):
    """Права на изменение объекта
    (суперюзер, администратор, модератор, автор).
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser
            or request.user.role == 'admin'
            or request.user.role == 'moderator'
            or obj.author == request.user
        )


class AdminOrReadOnlyPermission(permissions.BasePermission):
    """Права администратора, суперюзера и пользователя на чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.is_superuser
            )
        )
