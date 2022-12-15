from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    validate_slug)
from django.db import models

from .validators import UsernameRegexValidator, username_user, validate_year


class GenreAndCategoryModel(models.Model):
    """Genre."""

    slug = models.SlugField(
        'Slug',
        max_length=settings.LENG_SLUG,
        unique=True,
        validators=[validate_slug],
    )
    name = models.CharField(
        'Title',
        max_length=settings.LENG_MAX,
    )

    class Meta:
        abstract = True
        ordering = ('name', )

    def __str__(self):
        return self.name[:settings.LENG_CUT]


class ReviewAndCommentModel(models.Model):
    """ReviewAndComment."""

    text = models.CharField(
        'Review text',
        max_length=settings.LENG_MAX
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name='User'
    )
    pub_date = models.DateTimeField(
        'Date of publication of the review',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:settings.LENG_CUT]


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
        'Username',
        validators=(UsernameRegexValidator(), username_user),
        max_length=settings.LENG_DATA_USER,
        unique=True,
        blank=False,
        null=False,
        help_text=f'The set of characters is no more than {settings.LENG_DATA_USER}.'
                  'Only letters, numbers and @/./+/-/_',
        error_messages={
            'unique': "A user with that name already exists!",
        },
    )
    email = models.EmailField(
        'Email',
        max_length=settings.LENG_EMAIL,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        'Role',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    bio = models.TextField(
        'Biography',
        blank=True,
    )

    REQUIRED_FIELDS = ('email', )

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'
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

    class Meta(GenreAndCategoryModel.Meta):
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        default_related_name = 'categories'


class Genre(GenreAndCategoryModel):
    """Genre."""

    class Meta(GenreAndCategoryModel.Meta):
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'
        default_related_name = 'genres'


class Title(models.Model):
    """Title."""

    category = models.ForeignKey(
        Category,
        verbose_name='Category',
        on_delete=models.PROTECT,
        related_name='titles',
    )
    description = models.TextField(
        'Description',
        db_index=True,
        max_length=settings.LENG_MAX,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Genre',
        related_name='titles',
    )
    name = models.CharField(
        'Title',
        max_length=settings.LENG_MAX,
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        'Year of release',
        db_index=True,
        validators=(validate_year,),
    )

    class Meta:
        verbose_name = 'Composition'
        verbose_name_plural = 'Compositions'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(ReviewAndCommentModel):
    """Review."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Composition'
    )
    score = models.PositiveSmallIntegerField(
        'Assessment',
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

    class Meta(ReviewAndCommentModel.Meta):
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
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
        Review,
        on_delete=models.CASCADE,
        verbose_name='Review'
    )

    class Meta(ReviewAndCommentModel.Meta):
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        default_related_name = 'comments'