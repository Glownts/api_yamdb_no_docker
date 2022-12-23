from django.db import models
from django.conf import settings
from django.core.validators import validate_slug


class GenreAndCategoryModel(models.Model):
    """Base model for Genre and Category models."""

    name = models.CharField(
        unique=True,
        max_length=settings.LENG_MAX,
    )
    slug = models.SlugField(
        max_length=settings.LENG_SLUG,
        unique=True,
        validators=[validate_slug],
    )

    class Meta:
        abstract = True
        ordering = ('name', )

    def __str__(self):
        return self.name[:settings.LENG_CUT]


class ReviewAndCommentModel(models.Model):
    """Base model for Review and Comment."""

    text = models.CharField(
        max_length=settings.LENG_MAX
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:settings.LENG_CUT]
