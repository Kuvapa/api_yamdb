"""Models for Users app."""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLE_CHOICES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    )

    username = models.CharField(
        validators=(
            RegexValidator(regex=r'^[\w.@+-]+$',),
            RegexValidator(
                regex=r'^\b(m|M)(e|E)\b',
                inverse_match=True,
                message="""Данное имя пользователя использовать нельзя."""
            ),
        ),
        unique=True,
        max_length=150,
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Имя',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография',
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Права',
    )

    @property
    def is_admin(self):
        """Is_admin definition."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Is_moderator definition."""
        return self.role == self.MODERATOR or self.is_staff

    class Meta:
        """Meta for User."""

        ordering = ('id',)

    def __str__(self):
        """__str__ for User."""
        return self.username
