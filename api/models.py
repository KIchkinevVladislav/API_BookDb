from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    User Model
    """
    USER_ROLES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=25, unique=True, blank=False, null=False)
    bio = models.TextField(max_length=250, blank=True, null=True, verbose_name='Информация о пользователе')
    confirmation_code = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=15, choices=USER_ROLES, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    
class Genre(models.Model):
    """
    Genre Model.
    One book can be associated with several genres.
    """
    name = models.CharField(max_length=200, verbose_name="Жанр", unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name
 

class Book(models.Model):
    """
    Book Model.
    """
    title = models.TextField(verbose_name='Название')
    author = models.TextField(verbose_name='Автор')
    country = models.TextField(max_length= 25, verbose_name='Страна происхождения')
    description = models.TextField(verbose_name='Описание')
    rating = models.FloatField(blank=True, null=True, verbose_name='Рейтинг')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, blank=True, null=True, related_name='book', verbose_name='Жанр')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

        
class Review(models.Model):
    """
    Review Model.
    The review is for a book.
    """  
    text = models.TextField(verbose_name='Отзыв')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'ОТзыв от {self.author} на книгу {self.book}'

    
class Comment(models.Model):
    """
    Commetn Model.
    Users comment on the review.
    """  
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий от {self.author} к отзыву {self.review}'
