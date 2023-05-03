from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

from django.utils import timezone

User = get_user_model()
# Зададим переменную ROLE


class Category(models.Model):
    """Модель Категория"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        null=False,
        verbose_name='путь',
        help_text='Введите данные slug'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель Текста"""
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=255
    )
    description = models.TextField(
        verbose_name='Описание произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Genre',
        related_name='genres'
    )
    year = models.IntegerField(
        validators=[MaxValueValidator(timezone.now().year)], verbose_name='Год'
    )

    def __str__(self):
        return f'{self.name}: общая информация'


class Genre(models.Model):
    """Модель Жанра"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='путь',
        help_text='Введите данные slug'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель Ревью"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Reviews',
        verbose_name='Произведение Автора'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст Отзыва',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        db_index=True
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[MinValueValidator(1, 'Введите число от 1 до 10'),
                    MaxValueValidator(10, 'Введите число от 1 до 10')],
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Отзывы'
        unique_together = ('author', 'title',)


class Comment(models.Model):
    """Модель Комментариев"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
