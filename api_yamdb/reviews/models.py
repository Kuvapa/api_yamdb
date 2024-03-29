"""Models for api_yamdb."""
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Categories(models.Model):
    """Categories for reviews."""

    name = models.CharField(
        max_length=100,
        verbose_name='Название категории',
        help_text='Укажите название категории'
    )
    slug = models.SlugField(
        verbose_name='Уникальное название категории',
        help_text='Добавьте уникальный ID для категории',
        unique=True
    )

    class Meta:
        """Meta for Categories."""

        ordering = ('name', )

    def __str__(self):
        """__str__ for Categories."""
        return self.name


class Genres(models.Model):
    """Genres for reviews app."""

    name = models.CharField(
        max_length=100,
        verbose_name='Название Жанра',
        help_text='Укажите название жанра'
    )
    slug = models.SlugField(
        verbose_name='Уникальное название жанра',
        help_text='Добавьте уникальный ID для жанра',
        unique=True
    )

    class Meta:
        """Meta for Genres."""

        ordering = ('name', )

    def __str__(self):
        """__str__ for Genres."""
        return self.name


class Title(models.Model):
    """Titles for reviews app."""

    name = models.CharField(
        max_length=255,
        verbose_name='Название произведения',
        help_text='Укажите название произведения'
    )
    year = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(datetime.now().year)
        ],
        verbose_name='Год выпуска',
        help_text='Укажите год выпуска',
    )
    description = models.TextField(
        'Описание произведения',
        help_text='Введите описание'
    )
    genre = models.ManyToManyField(Genres)
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles'
    )

    class Meta:
        """Meta for Title."""

        ordering = ('name', )

    def __str__(self):
        """__str__ for Title."""
        return self.name


class Review(models.Model):
    """Review for reviews app."""

    title = models.ForeignKey(
        Title,
        verbose_name=('Произведения'),
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
        help_text='Напишите здесь текст нового отзыва'
    )
    author = models.ForeignKey(
        User,
        verbose_name=('Автор отзыва'),
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        default=None,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta for Review model."""

        ordering = ('pub_date',)
        constraints = [
            UniqueConstraint(fields=['author', 'title'],
                             name='unique_relationships'),
        ]


class Comments(models.Model):
    """Comments for reviews app."""

    review = models.ForeignKey(
        Review,
        verbose_name=('Отзыв'),
        on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите здесь текст нового комментария')
    author = models.ForeignKey(
        User,
        verbose_name=('Автор комментария'),
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta for Comments model."""

        ordering = ('pub_date',)
