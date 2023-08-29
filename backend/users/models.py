from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models

from foodgram.constants import (LENGTH_VALUE_FOR_EMAIL, LENGTH_VALUE_FOR_USER,
                                MIN_VALUE)
from users.validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_USER,
        unique=True,
        verbose_name='Уникальный юзернейм',
        validators=(
            UnicodeUsernameValidator(),
            MinLengthValidator(MIN_VALUE),
            validate_username
        )
    )
    email = models.EmailField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_EMAIL,
        unique=True,
        verbose_name='Адрес электронной почты',
    )
    first_name = models.CharField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_USER,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_USER,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        blank=False,
        max_length=LENGTH_VALUE_FOR_USER,
        verbose_name='Пароль',
    )

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    def __str__(self):
        return self.author.username

    class Meta:
        ordering = ['id']
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user',
                    'author'
                ),
                name='unique_follow'
            )
        ]
