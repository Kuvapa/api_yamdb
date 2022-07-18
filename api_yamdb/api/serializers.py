from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .validators import UniqueValueValidator

from users.models import User
from reviews.models import (
    Categories,
    Genres,
    GenresTitles,
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




class SlugObjectRelatedName(serializers.SlugRelatedField):
    def __init__(self, read_serializer_cls, **kwargs):
        super().__init__(**kwargs)
        self.read_serializer_cls = read_serializer_cls

    def to_representation(self, obj):
        return self.read_serializer_cls(obj).data


class TitleSerializer(serializers.ModelSerializer):
    category = SlugObjectRelatedName(
        read_serializer_cls=CategorySerializer,
        slug_field='slug',
        queryset=Categories.objects.all(),
    )
    genre = SlugObjectRelatedName(
        read_serializer_cls=GenreSerializer,
        slug_field='slug',
        read_only=True,
        required=False,
        many=True,
    )
    rating = serializers.SerializerMethodField()
    class Meta:
        model = Titles
        fields = '__all__'

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
        if isinstance(rating, int):
            return round(rating)
        return rating

    def create(self, validated_data):
        title = Titles.objects.create(**validated_data)
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
