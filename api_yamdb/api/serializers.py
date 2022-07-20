from django.db.models import Avg
from django.forms import ValidationError
from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.permissions import SAFE_METHODS

from .validators import UniqueValueValidator

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
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genres.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def create(self, validated_data):
        if 'genre' not in self.initial_data:
            title = Title.objects.create(**validated_data)
            return title
        genre = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genre)
        return title


class TitlesReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()
    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
        if isinstance(rating, int):
            return round(rating)
        return rating

    def create(self, validated_data):
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

    def validate(self, attrs):
        # import pdb; pdb.set_trace()
        if self.context['request'].method in SAFE_METHODS:
            return attrs
        if self.context['request'].method == 'PATCH':
            # import pdb; pdb.set_trace()
            if self.instance.author!=self.context['request'].user:
                raise PermissionDenied()
            return attrs
        if Review.objects.filter(
            author=self.context['request'].user,
            title=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise ValidationError("You can't make another review!")
        return attrs


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


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
