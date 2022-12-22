from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.role == 'admin' or request.user.is_superuser)
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and request.user.role == "admin")
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission


class AuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    @staticmethod
    def _is_moderator_or_admin(user):
        return (
            user.is_authenticated
            and (user.role == 'admin' or user.role == 'moderator')
        )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or self._is_moderator_or_admin(request.user)
        )
