from rest_framework import mixins, viewsets

from reviews.models import Categories, Genres, Titles
from .permissions import AdminOrReadOnlyPermission
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitlesReadSerializer,
                          TitleSerializer)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnlyPermission, )


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnlyPermission, )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnlyPermission, )

    def get_serializer_class(self):
        if self.action == 'list':
            return TitlesReadSerializer
        else:
            return TitleSerializer
