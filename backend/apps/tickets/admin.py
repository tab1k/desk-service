"""
Административная панель для заявок
"""
from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Ticket
    """
    list_display = ('id', 'title', 'status', 'priority', 'requester', 
                    'executor', 'created_at', 'completed_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'requester__username', 'executor__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Участники', {
            'fields': ('requester', 'executor')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
