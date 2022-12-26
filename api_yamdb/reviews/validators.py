"""
Валидации.
"""

from datetime import datetime

from django.core.exceptions import ValidationError


def validate_year(value):
    """Проверка года."""
    if value >= datetime.now().year:
        raise ValidationError(
            message=f'Year {value} more than current!',
            params={'value': value},
        )
