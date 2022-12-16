'''
Разрешения приложения api.
'''

from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    pass


class AuthorOrReadOnly(permissions.BasePermission):
    pass


class MeOrAdminOnly(permissions.BasePermission):
    pass
