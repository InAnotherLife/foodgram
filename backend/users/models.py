from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Модель кастомного пользователя. Авторизация пользователя происходит по 
    e-mail и паролю.
    """
    email = models.EmailField(
        verbose_name='E-mail',
        max_length=254,
        unique=True,
        blank=False
    )

    # Поле, которое используется в качестве имени пользователя при авторизации
    USERNAME_FIELD = 'email'
    # Обязательные поля для создания пользователя
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('email', 'username'),
                name='unique_email_username'
            )
        ]

    def __str__(self):
        return self.get_full_name()
