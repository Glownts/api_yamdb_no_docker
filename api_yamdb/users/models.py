from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    """
    Модель пользователя.

    Имеет поля ROLE_CHOICES, username, email, role, bio.

    ROLE_CHOICES определяет доступные варинаты для поля role,
    поле role отвечает за разрешения конкертного пользователя.

    username - имя пользователя, проходит валидацию и не может иметь
    значения, указанные в валидации.

    На указаный email высылается код подтверждения.

    Поле bio не является обязательным и заполняется пользователем отдельно.
    Это поле личной информации.
    """

    class Roles(models.TextChoices):
        USER = 'user', 'USER'
        ADMIN = 'admin', 'ADMIN'
        MODERATOR = 'moderator', 'MODERATOR'

    username = models.CharField(
        'username',
        validators=(UnicodeUsernameValidator(),),
        max_length=settings.LENG_DATA_USER,
        unique=True,
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
    )
    role = models.CharField(
        'role',
        max_length=settings.ROLE_LENG,
        choices=Roles.choices,
        default=Roles.USER,
        blank=True
    )
    bio = models.TextField(
        'biography',
        blank=True,
    )

    REQUIRED_FIELDS = ('email', )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            )
        ]

    @property
    def is_moderator(self):
        return self.role == self.Roles.MODERATOR

    @property
    def is_admin(self):
        return (
            self.role == self.Roles.ADMIN
            or self.is_superuser
            or self.is_staff)

    def __str__(self):
        return f'{self.username} {self.email} {self.role}'
