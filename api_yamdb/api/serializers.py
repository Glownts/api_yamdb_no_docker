from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField(read_only=True)

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


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(), many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


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

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        review_exists = Review.objects.filter(
            author=self.context['request'].user,
            title=title_id
        ).count()
        title = get_object_or_404(
            Title,
            id=title_id
        )

        if self.context['request'].method == 'POST' and review_exists:
            raise serializers.ValidationError(
                f'Отзыв на произведение {title.name} уже существует'
            )

        return data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            UnicodeUsernameValidator()
        ],
        max_length=settings.LENG_DATA_USER,
        required=True,
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        max_length=settings.LENG_EMAIL,
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


class UserCreationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UnicodeUsernameValidator()
        ],
        max_length=settings.LENG_DATA_USER,
        required=True,
    )
    email = serializers.EmailField(
        required=True,
        max_length=settings.LENG_EMAIL,
    )

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, data):
        if data in settings.BANNED_NAMES:
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве username.'
            )
        return data

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            existing = User.objects.get(email=data['email'])
            if existing.username != data['username']:
                raise serializers.ValidationError(
                    detail='This email already used'
                )
        if User.objects.filter(username=data['username']).exists():
            existing = User.objects.get(username=data['username'])
            if existing.email != data['email']:
                raise serializers.ValidationError(
                    detail='This name already used'
                )
        return data


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=settings.LENG_DATA_USER
    )
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username', 'confirmation_code',
        )
