'''
Разрешения приложения api.
'''

from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class AuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class MeOrAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                request.user.is_admin or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return (
                request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.is_superuser))

