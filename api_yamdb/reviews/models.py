from django.db import models

from users.models import User


class Categories(models.Model):
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
        ordering = ['name']

    def __str__(self):
        return self.name


class Genres(models.Model):
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
        ordering = ['name']

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название произведения',
        help_text='Укажите название произведения'
    )

    year = models.DateTimeField(
        verbose_name='Год выпуска',
        help_text='Укажите год выпуска',
        auto_now_add=True
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
    )

    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        default=None
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GenresTitles(models.Model):
    genre = models.ForeignKey(Genres, on_delete=models.CASCADE)
    title = models.ForeignKey(Titles, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre}, {self.title}'


class Review(models.Model):
    title = models.ForeignKey(
        Titles,
        verbose_name=("Произведения"),
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    text = models.TextField(
        verbose_name="Текст отзыва",
        help_text="Напишите здесь текст нового отзыва"
    )
    author = models.ForeignKey(
        User,
        verbose_name=("Автор отзыва"),
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    REVIEW_CHOICES = [(i, i) for i in range(1, 11)]
    score = models.CharField(
        max_length=2,
        choices=REVIEW_CHOICES,
        default=None,
    )
    pub_date = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    review = models.ForeignKey(
        Review,
        verbose_name=("Отзыв"),
        on_delete=models.CASCADE,
        related_name="comments")
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Напишите здесь текст нового комментария")
    author = models.ForeignKey(
        User,
        verbose_name=("Автор комментария"),
        on_delete=models.CASCADE,
        related_name="comments",
    )
    pub_date = models.DateTimeField(auto_now_add=True)
