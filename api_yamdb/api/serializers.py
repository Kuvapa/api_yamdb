from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .validators import UniqueValueValidator

from users.models import User
from reviews.models import (
    Categories,
    Genres,
    Titles,
    Comments,
    Review
)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
    )
    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UserReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор пользователя (чтение)."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role', )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genres.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all()
    )

    class Meta:
        model = Titles
        fields = '__all__'

    def create(self, validated_data):
        if 'genre' not in self.initial_data:
            title = Titles.objects.create(**validated_data)
            return title
        genre = validated_data.pop('genre')
        title = Titles.objects.create(**validated_data)
        title.genre.set(genre)
        return title


class TitlesReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Titles
        fields = '__all__'

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
        if isinstance(rating, int):
            return round(rating)
        return rating


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
