"""
Валидации.
"""

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


class UsernameValidator(UnicodeUsernameValidator):
    """Валидация поля username."""

    regex = r'@/./+/-/_'
    flags = 0
    max_length = settings.LENG_DATA_USER
    message = (f'Enter the correct username. It may contain:'
               f' only letters, numbers and signs @/./+/-/_.'
               f' Length not more than {settings.LENG_DATA_USER} symbols')
    error_messages = {
        'invalid': ('The set of symbols is no more '
                    f'than {settings.LENG_DATA_USER}. '
                    'Only letters, numbers and @/./+/-/_'),
        'required': 'The field cannot be empty',
    }

    def username_user(value):
        """Подтвержедение поля username."""
        banned = ['me']
        if str(value).lower() in banned:
            raise ValidationError(
                'Username is prohibited.'
            )