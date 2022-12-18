'''
Сериализаторы приложения api.

Не готовы!
'''

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.validators import UsernameRegexValidator

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
        fields = ('__all__')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('__all__')


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ('__all__')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('__all__')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('__all__')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UsernameRegexValidator()
        ],
        required=True,
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UsernameRegexValidator()
        ]
    )

    class Meta:
        model = User
        fields = ('__all__')


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UsernameRegexValidator()
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UsernameRegexValidator()

        ]
    )

    def validate_username(self, value):
        if value.lower() == "me":
            raise serializers.ValidationError("Username 'me' is not valid")
        return value

    class Meta:
        fields = ("username", "email")
        model = User


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code',
            'token')

    def get_token(self, obj):
        user = get_object_or_404(
            User,
            username=self.initial_data.get('username')
        )
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)