"""Views for API."""
import uuid

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import SAFE_METHODS
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Categories, Genres, Title, Review
from .filters import TitlesFilter
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitlesReadSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    UserReadOnlySerializer,
    SignUpSerializer,
    ConfirmationCodeSerializer
)
from .permissions import (
    AdminOnlyPermission,
    AdminOrReadOnlyPermission,
    AdminModeratorAuthorPermission
)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """API пользователя."""

    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = UserSerializer
    permission_classes = (AdminOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        """Me method ha-ha for UserViewSet."""
        if request.method == 'GET':
            serializer = UserReadOnlySerializer(request.user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = UserReadOnlySerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_confirmation_code(request):
    """Отправка кода подтверждения на почту."""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    confirmation_code = uuid.uuid3(uuid.NAMESPACE_DNS, user.email)
    send_mail(
        'Код подтверждения YAMDB',
        f'Код подтверждения: {confirmation_code}',
        'adminm@yamdb.ru',
        [user.email],
        fail_silently=False,
    )
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """Получение токена."""
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=serializer.data['username'])
    confirmation_code = serializer.data['confirmation_code']
    if User.objects.filter(username=user.username).exists():
        if confirmation_code != str(
            uuid.uuid3(uuid.NAMESPACE_DNS, user.email)
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token = AccessToken.for_user(user)
        return Response({f'token: {token}'}, status=status.HTTP_200_OK)
    else:
        return Response(
            {'username': 'Несуществующий пользователь.'},
            status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """CategoryViewSet for API."""

    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filterset_fields = ('name', )
    search_fields = ('=name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """GenreViewSet for API."""

    queryset = Genres.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filterset_fields = ('name', )
    search_fields = ('=name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """TitleViewSet for API."""

    queryset = Title.objects.all()
    permission_classes = (AdminOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filterset_class = TitlesFilter
    search_fields = ('=name',)

    def get_serializer_class(self):
        """Get_serializer_class method for TitleViewSet."""
        if self.action in ['list', 'retrieve']:
            return TitlesReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset for review."""

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ReviewSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )

    def get_title(self):
        """Get title object."""
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        """Queryset definition."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Create redefinition."""
        serializer.save(author=self.request.user, title=self.get_title())

    def get_permissions(self):
        """Get_permission method for ReviewViewSet."""
        if self.request.method == SAFE_METHODS:
            return (IsAuthenticatedOrReadOnly)
        elif self.request.method in ('PATCH', 'DELETE'):
            return (AdminModeratorAuthorPermission(),)
        return super(ReviewViewSet, self).get_permissions()


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset for comments."""

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )

    def get_title(self):
        """Get_title method for CommentViewSet."""
        return get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )

    def get_review(self):
        """Get_review method for CommentViewSet."""
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        """Get_queryset method for CommentViewSet."""
        review = Review.objects.filter(title=self.get_title(),
                                       pk=self.kwargs.get('review_id')).get()
        return review.comments.all()

    def perform_create(self, serializer):
        """Perform_create method for CommentViewSet."""
        serializer.save(author=self.request.user,
                        review=self.get_review())

    def get_permissions(self):
        """Get_permissions method for CommentViewSet."""
        if self.request.method in ('PATCH', 'DELETE'):
            return (AdminModeratorAuthorPermission(),)
        return super(CommentViewSet, self).get_permissions()
