from django.conf import settings
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator


from reviews.validators import UsernameRegexValidator
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User
)


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

    category = CategorySerializer(required=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField(required=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
            'rating'
        )
        read_only = ('id',)

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if rating is not None:
            rating = round(rating)
        return rating


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        many=False,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
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
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        max_length=settings.LENG_DATA_USER,
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.LENG_EMAIL,
    )

    bio = serializers.CharField(required=False)
    first_name = serializers.CharField(
        required=False,
        max_length=settings.LENG_DATA_USER
    )
    last_name = serializers.CharField(
        required=False,
        max_length=settings.LENG_DATA_USER
    )

    class Meta:
        model = User
        fields = ('__all__',)
        validators = [
            UniqueTogetherValidator(
                User.objects.all(), fields=['username', 'email']
            )
        ]

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        if self.context['request'].method == 'PATCH':
            path_username = self.context['view'].kwargs.get('username')

        if email and User.objects.filter(
            email=data['email']
        ).exists():
            existing = User.objects.get(email=data['email'])
            if username and existing.username != username:
                raise serializers.ValidationError(
                    detail='This email already used'
                )
            if path_username and existing.username != path_username:
                raise serializers.ValidationError(
                    detail='This email already used'
                )

        if username and User.objects.filter(
            username=username
        ).exists():
            existing = User.objects.get(username=data['username'])
            if email and existing.email != email:
                raise serializers.ValidationError(
                    detail='This name already used'
                )
        return data

    class Meta:
        abstract = True
        model = User
        fields = ('__all__')


class SignupSerializer(serializers.ModelSerializer):
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


class SelfSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        max_length=settings.LENG_DATA_USER,
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.LENG_EMAIL,
    )

    bio = serializers.CharField(required=False)
    first_name = serializers.CharField(
        required=False,
        max_length=settings.LENG_DATA_USER
    )
    last_name = serializers.CharField(
        required=False,
        max_length=settings.LENG_DATA_USER
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        validators = [
            UniqueTogetherValidator(
                User.objects.all(), fields=['username', 'email']
            )
        ]

    def validate(self, data):
        сurrent_user_email = self.instance.email
        сurrent_user_username = self.instance.username

        email = data.get('email')
        username = data.get('username')

        if email and User.objects.filter(
            email=email
        ).exists():
            existing = User.objects.get(email=data['email'])
            if existing.username != сurrent_user_username:
                raise serializers.ValidationError(
                    detail='This email already used'
                )

        if username and User.objects.filter(
            username=username
        ).exists():
            existing = User.objects.get(username=username)
            if existing.email != сurrent_user_email:
                raise serializers.ValidationError(
                    detail='This name already used'
                )
        return data


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        max_length=150,
    )

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, data):
        if data == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве username.'
            )
        return data

    def validate(self, data):
        if User.objects.filter(
            email=data['email']
        ).exists():
            existing = User.objects.get(email=data['email'])
            if existing.username != data['username']:
                raise serializers.ValidationError(
                    detail='мейл одинаковый, а ники разные'
                )
        if User.objects.filter(
            username=data['username']
        ).exists():
            existing = User.objects.get(username=data['username'])
            if existing.email != data['email']:
                raise serializers.ValidationError(
                    detail='ник одинаковый, а мейлы разные'
                )
        return data


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=settings.LENG_DATA_USER)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username', 'confirmation_code',
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'
