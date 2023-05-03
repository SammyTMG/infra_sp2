from .serializers import (
    SignUpSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleSerializerGet,
    ReviewSerializer,
    CommentSerializer,
    TokenSerializer,
    MeSerializer)
from .permissions import (ReadOnly, AdminOrModeratorOrAuthor, IsAdminOnly)
from core.utils import (CreateListDestroyViewsSet,)
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from reviews.models import Category, Genre, Title, Review, User
from django.db.models import Avg
from .filters import TitleFilter
from rest_framework import filters, status, viewsets
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


@api_view(['POST'])
def signup(request):
    """Регистрация нового пользователя"""
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    user_obj = User.objects.filter(Q(email=email) | Q(
        username=username)).first()
    if user_obj and user_obj.username != username:
        return Response('Отсутсвует обязательное поле или оно '
                        'некорректно',
                        status=status.HTTP_400_BAD_REQUEST)
    if user_obj and user_obj.email != email:
        return Response('Отсутсвует обязательное поле или оно '
                        'некорректно',
                        status=status.HTTP_400_BAD_REQUEST)
    user, created = User.objects.get_or_create(username=username, email=email)
    send_mail(subject='Подтверждение регистрации на сайте',
              message=f'{user.username} Ваш код {user.confirmation_code}',
              recipient_list=(user.email,),
              from_email=settings.DEFAULT_FROM_EMAIL)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    """Получение токена"""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    access_token = RefreshToken.for_user(user).access_token
    if user.confirmation_code != confirmation_code:
        return Response('Неверный код потверждения',
                        status=status.HTTP_400_BAD_REQUEST)
    return Response({'Token': f'Bearer {access_token}'})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOnly,)
    http_method_names = ('get', 'post', 'delete', 'patch')

    filter_backends = [filters.SearchFilter]
    lookup_field = 'username'
    search_fields = ('username',)

    @action(detail=False, methods=('get', 'patch'),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = MeSerializer(self.request.user,
                                  request.data,
                                  partial=True)
        serializer.is_valid(raise_exception=True)
        if request.method == 'PATCH':
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@action(detail=False, methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,))
def me(self, request):
    serializer = MeSerializer(self.request.user,
                              request.data,
                              partial=True)
    serializer.is_valid(raise_exception=True)
    if request.method == 'PATCH':
        serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = (Title.objects.annotate(rating=Avg('reviews__score'))
                .order_by('id'))
    serializer_class = TitleSerializer
    permission_classes = (ReadOnly,)
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializerGet
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminOrModeratorOrAuthor,)
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title().id)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user,
                               title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminOrModeratorOrAuthor,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class GenreViewSet(CreateListDestroyViewsSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewsSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    lookup_field = 'slug'
