"""Admin for Reviews app."""
from django.contrib import admin

from .models import Categories, Genres, Title, Review, Comments

admin.site.register(Categories)
admin.site.register(Genres)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comments)
