"""Serializers for API."""
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.forms import ValidationError
from django.core.exceptions import PermissionDenied
from rest_framework import serializers

from reviews.models import (
    Categories,
    Genres,
    Title,
    Comments,
    Review
)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        """Meta for UserSerializer."""

        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


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


class SlugObjectRelatedName(serializers.SlugRelatedField):
    """SlugObjectRelatedName for API."""

    def __init__(self, read_serializer_cls, **kwargs):
        """__init__  for SlugObjectRelatedName."""
        super().__init__(**kwargs)
        self.read_serializer_cls = read_serializer_cls

    def to_representation(self, obj):
        """To_representation method for SlugObjectRelatedName."""
        return self.read_serializer_cls(obj).data


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

    def create(self, validated_data):
        """Create method for TitleSerializer."""
        if 'genre' not in self.initial_data:
            title = Title.objects.create(**validated_data)
            return title
        genre = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genre)
        return title


class TitlesReadSerializer(serializers.ModelSerializer):
    """TitlesReadSerializer for API."""

    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        """Meta for TitlesReadSerializer."""

        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        """Get_rating method for TitlesReadSerializer."""
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
        if isinstance(rating, int):
            return round(rating)
        return rating

    def create(self, validated_data):
        """Create method for TitlesReadSerializer."""
        title = Title.objects.create(**validated_data)
        if 'genre' in self.initial_data:
            genres = self.initial_data.getlist('genre')
            for genre in genres:
                current_genre, _ = Genres.objects.get_or_create(slug=genre)
                title.genre.add(current_genre)
        return title


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
