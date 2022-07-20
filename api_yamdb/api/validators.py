"""Validators for api app in api_yamdb."""
from rest_framework import serializers


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
