"""ViewSets for api."""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
)
from api_yamdb.api_yamdb.reviews.models import Review

from reviews.models import Titles
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset for review."""

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
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

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)
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

