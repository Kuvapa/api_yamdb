"""Views for API."""
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
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
    SignUpSerializer,
    ConfirmationCodeSerializer
)
from .permissions import (
    AdminOnlyPermission,
    AdminOrReadOnlyPermission,
    UserSafeOrUpdatePermission
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
        """Информация о пользователе."""

        user = self.request.user
        serializer = self.get_serializer(user)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_confirmation_code(request):
    """Отправка кода подтверждения на почту."""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    confirmation_code = default_token_generator.make_token(user)
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
    user = User.objects.filter(username=serializer.data['username'])
    confirmation_code = serializer.data['confirmation_code']
    if user.exists():
        if confirmation_code != default_token_generator.check_token(
            user, confirmation_code
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token = AccessToken.for_user(user)
        return Response({f'token: {token}'}, status=status.HTTP_200_OK)
    else:
        return Response(
            {'username': 'Несуществующий пользователь.'},
            status=status.HTTP_404_NOT_FOUND)


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """CreateListDestroyViewSet definition."""

    pass


class CategoryViewSet(CreateListDestroyViewSet):
    """CategoryViewSet for API."""

    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filterset_fields = ('name', )
    search_fields = ('=name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
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

    queryset = Title.objects.all().annotate(rating=(Avg('reviews__score')))
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

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        UserSafeOrUpdatePermission,
    )
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


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset for comments."""

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        UserSafeOrUpdatePermission
    )
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )

    def get_review(self):
        """Get_review method for CommentViewSet."""
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        """Get_queryset method for CommentViewSet."""
        review = Review.objects.filter(title=self.kwargs.get('title_id'),
                                       pk=self.kwargs.get('review_id')).get()
        return review.comments.all()

    def perform_create(self, serializer):
        """Perform_create method for CommentViewSet."""
        serializer.save(author=self.request.user,
                        review=self.get_review())
