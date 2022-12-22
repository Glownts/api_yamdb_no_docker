from django.conf import settings
from django.db.models import Avg


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
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


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

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

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if rating is not None:
            rating = round(rating)
        return rating


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

        if self.context['request'].method == 'POST' and review_exists:
            raise serializers.ValidationError

        return data


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
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
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
        max_length=settings.LENG_EMAIL,
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        max_length=settings.LENG_DATA_USER,
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
                    detail='This email already used'
                )
        if User.objects.filter(
            username=data['username']
        ).exists():
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
