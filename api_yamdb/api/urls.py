'''
URLs приложения api.

router.urls включает адреса для доступа api к
моделям проекта. djoser.urls и djoser.urls.jwt
включают адреса для регистрации и аутентификации
пользователя; получения, обновления и проверки
валидности токена.
'''

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>.+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>.+)/reviews/(?P<review_id>.+)/comments',
                CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
]
