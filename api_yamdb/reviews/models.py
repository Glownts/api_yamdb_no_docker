"""
Модели приложения reviews.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import GenreAndCategoryModel, ReviewAndCommentModel
from users.models import User

from .validators import validate_year


class Category(GenreAndCategoryModel):
    """
    Модель категорий произведений.

    Основывается на базовой модели GenreAndCategoryModel.
    Определяет поля name и slug.
    """


class Genre(GenreAndCategoryModel):
    """
    Модель жанров произведений.

    Основывается на базовой модели GenreAndCategoryModel.
    Определяет поля name и slug.
    """


class Title(models.Model):
    """
    Модель произведений.

    Определяет поля name, year, category, description и
    genre.

    name - название произведения;
    year - дата выхода;
    category - id категории, к которой относится данное произведение;
    genre - id жанра, к которому относится данное произведение;
    description - необязательное поле - подробное описание произведения.
    """

    name = models.CharField(
        'title',
        max_length=settings.LENG_MAX,
        help_text='Введите название произведения'
    )
    year = models.PositiveSmallIntegerField(
        'year of release',
        validators=(validate_year,),
    )
    category = models.ForeignKey(
        Category,
        help_text='Категория, к которой будет относиться произведение',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
    )
    description = models.TextField(
        'description',
        max_length=settings.LENG_MAX,
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='genretitle',
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(ReviewAndCommentModel):
    """
    Модель отзыва на произведение.

    Определяет поля title, score и author.

    title - id произведения, на который написан отзыв;
    score - оценка произведения от 1 до 10, стандартное значение 5;
    author  - id автора комментария.
    """

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        'score',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={
            'validators': 'Score from 1 to 10!'
        },
        default=5
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta(ReviewAndCommentModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review',
            )
        ]


class Comment(ReviewAndCommentModel):
    """
    Модель комментария к отзыву на произведение.

    Определяет поля review и author.

    review - id отзыва, к котормоу написан комментарий;
    author  - id автора комментария.
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='comments')
