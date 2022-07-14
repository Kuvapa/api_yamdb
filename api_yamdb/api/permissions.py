"""Custom permissions for api."""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Access prmission for correcting obj by only the author."""

    def has_object_permission(self, request, view, obj):
        """Permission method definition."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user