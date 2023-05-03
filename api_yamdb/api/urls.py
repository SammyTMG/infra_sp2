from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (TitleViewSet,
                    CategoryViewSet,
                    GenreViewSet,
                    UserViewSet,
                    ReviewViewSet,
                    CommentViewSet)

from . import views


v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('categories', CategoryViewSet)
v1_router.register('titles', TitleViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='viewsets'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/signup/', views.signup, name='signup'),
    path('v1/auth/token/', views.get_token,
         name='get_token'),
]
