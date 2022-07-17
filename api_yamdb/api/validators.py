from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def email_validator(email):
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError('Email неккоректный.')


def yamdb_user_validator(username):
    try:
        username != 'me'
    except ValidationError:
        raise ValidationError('Email неккоректный.')
