import re

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


def validate_username(value):
    if value == 'me':
        raise serializers.ValidationError('Нельзя использовать имя me')
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise serializers.ValidationError('Required. 150 characters or '
                                          'fewer. Letters, digits '
                                          'and @/./+/-/_ only.')
    return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(max_length=150, required=True,
                                     validators=[validate_username])


class TokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(max_length=150, required=True,
                                     validators=[validate_username])


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150, required=True,
        validators=[UniqueValidator(queryset=User.objects.all()),
                    validate_username])

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class MeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug')
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError(' Год выпуска не может быть'
                                              'больше текущего')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Вы уже оставили отзыв на это произведение')
        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        model = Comment


class TitleSerializerGet(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title
