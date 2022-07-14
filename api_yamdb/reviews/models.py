"""Review app models."""
# Users, Titles, Categories, Genres, Review и Comments. 
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Titles(models.Model):
    pass

class Categories(models.Model):
    pass

class Genres(models.Model):
    pass

class Review(models.Model):
    # id,title_id,text,author,score,pub_date
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
    REVIEW_CHOICES = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    ]
    score = models.CharField(
        max_length=2,
        choices=REVIEW_CHOICES,
        default=None,
    )
    pub_date = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    # id,review_id,text,author,pub_date
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