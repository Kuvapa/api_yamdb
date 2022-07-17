from rest_framework import mixins, viewsets
from django.shortcuts import get_object_or_404

from reviews.models import Categories, Genres, Titles, Review
from .permissions import AdminOrReadOnlyPermission
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitlesReadSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer
)


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


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset for review."""

    permission_classes = (AdminOrReadOnlyPermission,)
    serializer_class = ReviewSerializer

    def get_title(self):
        """Get title object."""
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Titles, id=title_id)

    def get_queryset(self):
        """Queryset definition."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Create redefinition."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset for comments."""

    permission_classes = (AdminOrReadOnlyPermission,)
    serializer_class = CommentSerializer

    def get_post(self):
        """Get review object."""
        review_id = self.kwargs.get("review_id")
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        """Queryset definition."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Create redefinition."""
        serializer.save(author=self.request.user, review=self.get_review())

