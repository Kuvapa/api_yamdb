from django.core.exceptions import ValidationError


def yamdb_username_validator(username):
    if username == 'me':
        raise ValidationError('Данное имя пользователя использовать нельзя.')
