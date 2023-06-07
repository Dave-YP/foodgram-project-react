from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя.

    """
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} {self.email}'


class Subscription(models.Model):
    """
    Модель, представляющая подписку между двумя пользователями.

    """

    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            )
        ]

    def __str__(self):

        return f'{self.user.username} подписан на {self.author.username}'
