import random
from rest_framework import serializers
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    AuthenticationFailed,
)
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Genre, Book, Review, Comment


def get_tokens_for_user(user):
    """
    Creating a token for the user manually.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_code():
    """
    Code generation for confirmation_code.
    """
    random.seed()
    return str(random.randint(10000000, 99999999))   


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serialization of data during user registration.
    Create confirmation_code.
    """
    class Meta:
        model = User
        fields = ('email',)

    def validate(self, data):
        confirmation_code = generate_code()
        data['confirmation_code'] = confirmation_code
        return data

    
class TokenSerializer(serializers.ModelSerializer):
    """
    Serialization at user login.
    Checking the confirmation_code.
    """
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = (
            'email',
            'confirmation_code',
        )

    def validate(self, data):
        email = data['email']
        confirmation_code = data['confirmation_code']
        profile = get_object_or_404(User, email=email)
        if profile.confirmation_code != confirmation_code:
            raise ValidationError('ошибка')
        else:
            token = get_tokens_for_user(profile)
            data['token'] = token
        return data

    
class UserSerializer(serializers.ModelSerializer):
    """ 
    Serializer for User model.
    """
    class Meta:
        fields = ('email', 'username', 'bio', 'role', 'first_name', 'last_name',)
        model = User

        
class GenreSerializer(serializers.ModelSerializer):
    """ 
    Serializer for Genre model.
    """
    class Meta:
        fields = ('name', 'slug',)
        model = Genre
        lookup_field = 'slug'
        

class CustomSlugRelatedField(serializers.SlugRelatedField):
    """
    Genre serializer for BookSerializerю
    """
    def to_representation(self, value):
        return {'name': value.name, 'slug': value.slug}


class BookSerializer(serializers.ModelSerializer):
    """ 
    Serializer for Book model.
    """
    genre = CustomSlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=False
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'title', 'author', 'country', 'rating',
                  'description', 'genre',)    
        model = Book   

        
class ReviewSerializer(serializers.ModelSerializer):
    """ 
    Serializer for Review model.
    Review creation and editing functions.
    User can only make one review.
    """
    author = serializers.ReadOnlyField(source='author.username')
    title = serializers

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review

    def create(self, validated_data):
        author = self.context['request'].user
        request = self.context.get('request')
        book_id = request.parser_context['kwargs']['books_pk']
        method = request.method
        book = get_object_or_404(Book, pk=book_id)
        review = Review.objects.filter(book_id=book_id, author=author)
        if method == 'POST' and review:
            raise ValidationError('Можно оставить только один отзыв')
        return Review.objects.create(**validated_data)

    def update(self, instance, validated_data):
        print(instance)
        author = self.context['request'].user
        if not author.is_authenticated:
            raise AuthenticationFailed()
        if instance.author != author:
            raise PermissionDenied()
        instance.text = validated_data.get('text', instance.text)
        instance.score = validated_data.get('score', instance.score)
        instance.pub_date = validated_data.get('pub_date', instance.pub_date)
        instance.save()
        return instance

    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    """ 
    Serializer for Comment model.
    """
    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment
        
