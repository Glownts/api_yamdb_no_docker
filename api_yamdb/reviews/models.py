from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from core.models import GenreAndCategoryModel, ReviewAndCommentModel

from .validators import UsernameRegexValidator, username_user, validate_year


class User(AbstractUser):

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLE_CHOICES = (
        (USER, 'user'),
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator'),
    )

    username = models.CharField(
        'username',
        validators=(UsernameRegexValidator(), username_user),
        max_length=settings.LENG_DATA_USER,
        unique=True,
        blank=False,
        null=False,
        help_text=('The set of characters is no more '
                   f'than {settings.LENG_DATA_USER}.'
                   'Only letters, numbers and @/./+/-/_'),
        error_messages={
            'unique': "A user with that name already exists!",
        },
    )
    email = models.EmailField(
        'email',
        max_length=settings.LENG_EMAIL,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        'role',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    bio = models.TextField(
        'biography',
        blank=True,
    )

    REQUIRED_FIELDS = ('email', )

    class Meta:
        ordering = ('id',)
        verbose_name = 'user'
        verbose_name_plural = 'users'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            )
        ]

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    def __str__(self):
        return f'{self.username} {self.email} {self.role}'


class Category(GenreAndCategoryModel):
    """Category."""

    name = models.CharField(
        unique=True,
        max_length=256,
        verbose_name='Наименование',
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-id',)

    def __str__(self):
        return self.name[:15]

class Genre(GenreAndCategoryModel):
    """Genre."""

    name = models.CharField(
        unique=True,
        max_length=256,
        verbose_name='Наименование',
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('-id',)

    def __str__(self):
        return self.name[:15]


class Title(models.Model):
    """Title."""

    name = models.CharField(
        'title',
        max_length=settings.LENG_MAX,
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        'year of release',
        db_index=True,
        validators=(validate_year,),
    )
    category = models.ForeignKey(
        Category,
        verbose_name='category',
        on_delete=models.PROTECT,
        related_name='titles',
    )
    description = models.TextField(
        'description',
        db_index=True,
        max_length=settings.LENG_MAX,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        through='genretitle',
        verbose_name='Genre',
    )

    class Meta:
        verbose_name = 'title'
        verbose_name_plural = 'titles'
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):

    title = models.ForeignKey(
        to=Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название произведения'
    )
    text = models.TextField(
        verbose_name='Текст отзыва')
    score = models.PositiveSmallIntegerField(
        'score',
        db_index=True,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={
            'validators': 'Score from 1 to 10!'
        },
        default=1
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='user',
        related_name='author'
    )

    class Meta(ReviewAndCommentModel.Meta):
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review',
            )
        ]


class Comment(ReviewAndCommentModel):
    """Comment."""

    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв')
    text = models.TextField(
        verbose_name='Текст комментария')
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментирования')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-review', '-id',)

    def __str__(self):
        return f'{self.author}: {self.text[:33]}'
