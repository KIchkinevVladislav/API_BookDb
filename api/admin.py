from django.contrib import admin

from .models import Genre, Book, Review, Comment, User

admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(User)
