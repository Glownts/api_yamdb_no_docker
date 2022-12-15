'''
Сериализаторы приложения api.

Не готовы!
'''

from rest_framework import serializers

from reviews.models import (
    Category,
    Comment,
    Genre,
    User,
    Review,
    Title
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('__all__',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('__all__',)


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ('__all__',)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('__all__',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('__all__',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__',)
