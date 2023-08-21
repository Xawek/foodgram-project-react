from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        blank=False,
        max_length=150,
        unique=True,
        verbose_name='Уникальный юзернейм',
        validators=[UnicodeUsernameValidator(), ]
    )
    email = models.EmailField(
        blank=False,
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты',
    )
    first_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        blank=False,
        max_length=150,
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
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Подписка'
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
