from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.validators import UsernameRegexValidator
from rest_framework_simplejwt.tokens import RefreshToken


from reviews.models import (
    Category,
    Comment,
    Genre,
    User,
    Review,
    Title
)

from reviews.validators import UsernameRegexValidator


class CategorySerializer(serializers.ModelSerializer):
    """Sterilizer for categories of works."""

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):
    """Sterilizer for genres."""

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    """Sterilizer for returning the list of works."""

    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(required=True)
    genre = GenreSerializer(many=True, read_only=True)
    year = serializers.IntegerField(required=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year',
            'rating', 'description',
            'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        many=False,
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only = ('id',)

    def validate(self, data):
        request = self.context.get('request')

        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            title = get_object_or_404(Title, pk=title_id)
            if Review.objects.filter(
                    author=request.user, title=title
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for working with comments."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only = ('review',)


class UserSerializer(serializers.ModelSerializer):

    """Serializer for new users."""

    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UsernameRegexValidator()
        ]
    )

    class Meta:
        abstract = True
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
            raise serializers.ValidationError('Username "me" is not valid')
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
            'token'
        )

    def get_token(self, obj):
        user = get_object_or_404(
            User,
            username=self.initial_data.get('username')
        )
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)