"""Serializers for api app in api_yamdb."""
from rest_framework import serializers

from reviews.models import Review, Comments
from .validators import UniqueValueValidator


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        """Meta for ReviewSerializer."""

        model = Review
        fields = '__all__'
        read_only_fields = ('title',)
        validators = [
            UniqueValueValidator('title')
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for commentss."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        """Meta for CommentSerializer."""

        model = Comments
        fields = '__all__'
        read_only_fields = ('review',)
        validators = [
            UniqueValueValidator('review')
        ]
