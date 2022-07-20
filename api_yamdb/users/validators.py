"""Validators for Users app."""
from django.core.exceptions import ValidationError


def yamdb_username_validator(username):
    """Yamdb_username_validator for User app."""
    if username == 'me':
        raise ValidationError('Данное имя пользователя использовать нельзя.')
