from rest_framework import permissions


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class AuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    @staticmethod
    def _is_moderator_or_admin(user):
        return (
            user.is_authenticated
            and (user.is_admin
                 or user.is_moderator
                 or user.is_superuser)
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
