from django.db import models
from django.conf import settings
from django.core.validators import validate_slug


class GenreAndCategoryModel(models.Model):
    """Base model for Genre and Category models."""

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
    """Base model for Review and Comment."""

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
