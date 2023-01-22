from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    TokenView,
    UserViewSet,
    BookViewSet, 
    GenreViewSet,
    ReviewViewSet,
    CommentViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'books', BookViewSet, basename='books')
review_router = routers.NestedSimpleRouter(router, r'books', lookup='books')
review_router.register(r'reviews', ReviewViewSet, basename='reviews')
comment_router = routers.NestedSimpleRouter(review_router, r'reviews', lookup='review')
comment_router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(review_router.urls)),
    path('v1/', include(comment_router.urls)),
    path('v1/auth/email/', RegisterView.as_view(),
        name='get_confirmation_code'),
    path('v1/auth/token/', TokenView.as_view(), name='get_token'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
