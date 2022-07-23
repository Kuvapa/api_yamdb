"""Serializers for API."""
from django.forms import ValidationError
from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User
from reviews.models import (
    Categories,
    Genres,
    Title,
    Comments,
    Review
)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )
    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )

    class Meta:
        """Meta for UserSerializer."""

        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UserReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор пользователя (чтение)."""

    class Meta:
        """Meta for UserReadOnlySerializer."""

        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role', )


class CategorySerializer(serializers.ModelSerializer):
    """CategorySerializer for API."""

    class Meta:
        """Meta for CategorySerializer."""

        model = Categories
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """GenreSerializer for API."""

    class Meta:
        """Meta for GenreSerializer."""

        model = Genres
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """TitleSerializer for API."""

    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genres.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all()
    )

    class Meta:
        """Meta for TitleSerializer."""

        model = Title
        fields = '__all__'


class TitlesReadSerializer(serializers.ModelSerializer):
    """TitlesReadSerializer for API."""

    rating = serializers.FloatField(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        """Meta for TitlesReadSerializer."""

        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        """Meta for ReviewSerializer."""

        model = Review
        fields = '__all__'
        read_only_fields = ('title',)
        ordering = ['id']

    def validate(self, attrs):
        """Validate method for ReviewSerializer."""
        if self.context['request'].method == 'PATCH':
            if self.instance.author != self.context['request'].user:
                raise PermissionDenied()
            return attrs
        elif Review.objects.filter(
            author=self.context['request'].user,
            title=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise ValidationError("You can't make another review!")
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """CommentSerializer for API."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        """Meta for CommentSerializer."""

        exclude = ('review',)
        model = Comments
        read_only_fields = ('review',)
        ordering = ['id']


class SignUpSerializer(serializers.ModelSerializer):
    """SignUpSerializer for API."""

    class Meta:
        """Meta for SignUpSerializer."""

        model = User
        fields = ('email', 'username')


class ConfirmationCodeSerializer(serializers.Serializer):
    """ConfirmationCodeSerializer for API."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
