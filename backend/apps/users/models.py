"""
Модель пользователя с поддержкой ролей
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Расширенная модель пользователя с ролями
    """
    
    class Role(models.TextChoices):
        REQUESTER = 'REQUESTER', 'Заявитель'
        OPERATOR = 'OPERATOR', 'Оператор'
        EXECUTOR = 'EXECUTOR', 'Исполнитель'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REQUESTER,
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Отдел'
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
