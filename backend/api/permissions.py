from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """Права доступа: Администратор."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin


class ReadOnly(BasePermission):
    """Права доступа: Чтение."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    """Права доступа: Автор."""

    def has_object_permission(self, request, view, obj):
        return request.user and request.user == obj.author
