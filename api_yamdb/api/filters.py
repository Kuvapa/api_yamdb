"""Filters for API."""
from django_filters import rest_framework as filters

from reviews.models import Title


class TitlesFilter(filters .FilterSet):
    """Titles filter."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='icontains'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )

    class Meta:
        """Meta for Titles filter."""

        model = Title
        fields = ('name', 'year', 'genre', 'category')
