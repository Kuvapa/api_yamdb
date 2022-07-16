import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserSerializer, UserReadOnlySerializer
from .permissions import AdminOnlyPermission
from .validators import email_validator, yamdb_user_validator


User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
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
