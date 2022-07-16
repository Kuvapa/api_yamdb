from rest_framework import serializers
from django.db.models import Avg

from reviews.models import Categories, Genres, GenresTitles, Titles


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
    )
    genres = GenreSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Titles
        fields = ('__all__')

    def create(self, validated_data):
        if 'genres' not in self.initial_data:
            title = Titles.objects.create(**validated_data)
            return title
        else:
            genres = validated_data.pop('genres')
            title = Titles.objects.create(**validated_data)
            for genre in genres:
                current_genre, status = Genres.objects.get_or_create(
                    **genre)
                GenresTitles.objects.create(
                    genres=current_genre, titles=title)
            return title


class TitlesReadSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(read_only=True, many=True)
    categories = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Titles

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
        if isinstance(rating, int):
            return round(rating)
        return rating
