
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework.response import Response
from rest_framework import viewsets, filters, permissions, generics, pagination
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.core.mail import send_mail
from .models import User, Genre, Book, Review, Comment

from rest_framework.mixins import (
    CreateModelMixin, 
    DestroyModelMixin,
    ListModelMixin)

from .serializers import (
    UserSerializer,
    GenreSerializer,
    BookSerializer, 
    ReviewSerializer,
    CommentSerializer,
    RegisterSerializer,
    TokenSerializer,
)
from .filter import BookFilterBackend
from .permissions import (
    IsAdminUser,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrModerator,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class RegisterView(generics.CreateAPIView):
    """
    A cconfirmation_code is sent to the mail received from the user
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.confirmation_code = serializer.validated_data[
                'confirmation_code'
            ]
            serializer.email = serializer.validated_data['email']
            serializer.save()
            send_mail(
                'Авторизация',
                f'confirmation_code = {serializer.confirmation_code} email = {serializer.email}',
                'admin@m.mi',
                [f'{serializer.email}'],
                fail_silently=False,
            )
        return Response(serializer.data)

    
class TokenView(APIView):
    """
    Sending the generated token to the user
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'token': serializer.validated_data['token']})

        
class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for working with users
    Function get_or_update_self allows the user to change information about himself
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = pagination.PageNumberPagination 
    permission_classes = [IsAdminUser, permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'name',
    ]
    lookup_field = 'username'

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,), methods=['get', 'patch'], url_path='me')
    def get_or_update_self(self, request):
        if request.method != 'GET':
            serializer = self.get_serializer(
                instance=request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(request.user, many=False)
            return Response(serializer.data)

        
class GenreViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Viewing the list, creating and deleting genres
    """
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name']
    lookup_field = 'slug'

    
class BookViewSet(viewsets.ModelViewSet):
    """
    CRUD for Book
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [BookFilterBackend]
    filterset_fields = ['title', 'author', 'country', 'genre']
    

class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD for Review
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrAdminOrModerator]

    def get_book(self):
        book = get_object_or_404(Book, id=self.kwargs['books_pk'])
        return book
    
    def get_queryset(self):
        queryset = Review.objects.filter(book=self.get_book())
        return queryset
    
    def update_rating(self):
        book = get_object_or_404(Book, id=self.kwargs['books_pk'])
        average_rating = Review.objects.filter(book=book).aggregate(Avg('score'))
        book.rating = round(average_rating['score__avg'], 1)
        book.save

    def perform_create(self, serializer):
        pk = self.kwargs.get('books_pk')
        book = get_object_or_404(Book, pk=self.kwargs.get('books_pk'))
        serializer.save(author=self.request.user, book_id=self.kwargs.get('books_pk'))
        self.update_rating()

    def perform_update(self, serializer):
        serializer.save()
        self.update_rating

    def perform_destroy(self, instance):
        instance.delete()
        self.update_rating

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrModerator, IsAuthenticatedOrReadOnly]

    def get_review(self):
        review = get_object_or_404(Review, id=self.kwargs['review_pk'])
        return review

    def get_queryset(self):
        queryset = Comment.objects.filter(review=self.get_review()).all()
        return queryset

    def perform_create(self, serializer):
        reviews = get_object_or_404(Review, pk=self.kwargs.get('review_pk'))
        serializer.save(
        author=self.request.user, review_id=self.kwargs.get('review_pk')
    )
