from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models

from .validators import yamdb_username_validator


ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'

ROLE_CHOICES = (
    (ADMIN, 'Администратор'),
    (MODERATOR, 'Модератор'),
    (USER, 'Пользователь'),
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        validators=(yamdb_username_validator,),
        unique=True,
        max_length=150,
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        validators=(validate_email,),
        unique=True,
        max_length=254,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Фамилия',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография',
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='user'
    )

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username
