"""Validators for api app in api_yamdb."""
from rest_framework import serializers
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


class UniqueValueValidator:
    """UniqueValue validator."""

    def __init__(self, *fields):
        """Keys for values dict."""
        self.fields = fields

    def __call__(self, values):
        """Values validation."""
        fields_count = {values[field] for field in self.fields}
        if len(fields_count) != len(self.fields):
            raise serializers.ValidationError('Unique field error!')
