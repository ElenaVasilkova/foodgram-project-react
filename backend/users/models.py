from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username

USER = 'user'
ADMIN = 'admin'


class User(AbstractUser):
    """Полнофункциональная модель пользователя."""
    ROLES = ((USER, USER), (ADMIN, ADMIN))
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Имя пользователя',
        help_text='Введите имя пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        db_index=True,
        blank=False,
        null=False,
        verbose_name='Адрес электронной почты',
        help_text='Введите адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя',
        help_text='Введите имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия',
        help_text='Введите фамилию'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'@{self.username}: {self.email}.'

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser

    @property
    def is_user(self):
        return self.is_user


class Subscribe(models.Model):
    """Модель связи пользователя и автора для реализации системы подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribing')
        ]

    def __str__(self):
        return (f'Пользователь {self.user} '
                f'подписан на {self.author}')
