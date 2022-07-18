import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Categories, Genres, Titles, Review
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    UserReadOnlySerializer
)
from .permissions import (
    AdminOnlyPermission,
    AdminOrReadOnlyPermission,
)
from .validators import email_validator, yamdb_user_validator


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """API пользователя."""

    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = UserSerializer
    permission_classes = (AdminOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me')
    def own_account(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.role == 'admin':
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = UserReadOnlySerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


@api_view(['POST'])
def send_confirmation_code(request):
    """Отправка кода подтверждения на почту."""

    email = request.data.get('email')
    username = request.data.get('username')
    if email:
        email_validator(email)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if username:
        yamdb_user_validator(username)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    User.objects.get_or_create(
        email=email,
        username=username,
    )
    confirmation_code = uuid.uuid3(uuid.NAMESPACE_DNS, email)
    send_mail(
        'Код подтверждения YAMDB',
        f'Код подтверждения: {confirmation_code}',
        'adminm@yamdb.ru',
        [email],
        fail_silently=False,
    )
    return Response({'email': email}, {'username': username})


@api_view(['POST'])
def get_token(request):
    """Получение токена."""
    email = request.data.get('email')
    email_validator(email)
    user = get_object_or_404(User, email=email)
    confirmation_code = request.data.get('confirmation_code')
    if confirmation_code != str(uuid.uuid3(uuid.NAMESPACE_DNS, email)):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    token = default_token_generator.make_token(user)
    return Response({f'token: {token}'}, status=status.HTTP_200_OK)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
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
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filterset_fields = ('name', )
    search_fields = ('=name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filterset_fields = ('year',)
    search_fields = ('^name',)
    serializer_class = TitleSerializer

    def get_queryset(self):
        query = Titles.objects.all()
        genre = self.request.query_params.get('genre')
        if genre is not None:
            query = query.filter(genre__slug=genre)
        category = self.request.query_params.get('category')
        if category is not None:
            query = query.filter(category__slug=category)
        name = self.request.query_params.get('name')
        if name is not None:
            query = query.filter(name__startswith=name)
        return query


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
