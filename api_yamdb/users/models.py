import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.core.exceptions import ValidationError
import re


def validate_user_name(value):
    reg = re.compile(r'^[\w.@+-]+\Z')
    if not reg.match(value):
        raise ValidationError(
            u'%s Отсутствует обязательное поле или оно некорректно'
        )


class UserYambd(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    USERS_ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]
    role = models.CharField(
        max_length=254,
        choices=USERS_ROLE_CHOICES,
        default=USER,
    )
    email = models.EmailField(unique=True,)
    username = models.CharField(max_length=150, unique=True,
                                validators=[validate_user_name],
                                blank=False, null=False)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    confirmation_code = models.TextField(default=uuid.uuid4, editable=False,)

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_name'
            ),
        ]
