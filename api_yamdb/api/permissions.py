from django.contrib.auth import get_user_model
from rest_framework import permissions


User = get_user_model()


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and (
                request.user.role == User.ADMIN
                or request.user.is_superuser))
        )


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.role == User.ADMIN
                 or request.user.is_superuser)
        )


class AdminOrModeratorOrAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == User.MODERATOR
            or request.user.role == User.ADMIN
            or obj.author == request.user
        )
