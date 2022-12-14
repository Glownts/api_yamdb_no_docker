from datetime import datetime

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


class UsernameRegexValidator(UnicodeUsernameValidator):
    """User Name Validation."""

    flags = 0
    max_length = settings.LENG_DATA_USER
    message = (f'Enter the correct username. It may contain:'
               f' only letters, numbers and signs @/./+/-/_.'
               f' Length not more than {settings.LENG_DATA_USER} symbols')
    error_messages = {
        'invalid': f'The set of symbols is no more than {settings.LENG_DATA_USER}. '
                   'Only letters, numbers and @/./+/-/_',
        'required': 'The field cannot be empty',
    }


def username_user(value):
    """User Name verification."""
    if value == 'me':
        raise ValidationError(
            'User name not found.'
        )
    return value
        

def validate_year(value):
    """Checking the year."""
    if value >= datetime.now().year:
        raise ValidationError(
            message=f'Year {value} more than current!',
            params={'value': value},
        )