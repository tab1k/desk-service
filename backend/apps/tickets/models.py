"""
Модель заявки
"""
from django.db import models
from django.conf import settings


class Ticket(models.Model):
    """
    Модель заявки в службу поддержки
    """
    
    class Status(models.TextChoices):
        NEW = 'NEW', 'Новая'
        ASSIGNED = 'ASSIGNED', 'Назначена'
        IN_PROGRESS = 'IN_PROGRESS', 'В работе'
        COMPLETED = 'COMPLETED', 'Выполнена'
        CLOSED = 'CLOSED', 'Закрыта'
    
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Низкий'
        MEDIUM = 'MEDIUM', 'Средний'
        HIGH = 'HIGH', 'Высокий'
        URGENT = 'URGENT', 'Срочный'
    
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус'
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name='Приоритет'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets',
        verbose_name='Заявитель'
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets',
        null=True,
        blank=True,
        verbose_name='Исполнитель'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата выполнения'
    )
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"#{self.pk} - {self.title} ({self.get_status_display()})"
