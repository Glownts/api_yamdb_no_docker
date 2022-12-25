"""
Вспомогательные функции приложения api.
"""

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings


def mail_confirmation(request, user):
    """Подтверждение на почту."""

    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        'Тема письма',
        confirmation_code,
        settings.MAIL,
        [user.email],
        fail_silently=False,
    )
