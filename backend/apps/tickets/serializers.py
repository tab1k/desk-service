"""
Сериализаторы для заявок
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Ticket
from apps.users.serializers import UserSerializer


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания заявки
    """
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'priority')
    
    def create(self, validated_data):
        # Автоматически устанавливаем заявителя из текущего пользователя
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)


class TicketListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка заявок
    """
    requester = UserSerializer(read_only=True)
    executor = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = ('id', 'title', 'description', 'status', 'status_display',
                  'priority', 'priority_display', 'requester', 'executor',
                  'created_at', 'updated_at', 'completed_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'completed_at')


class TicketDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального просмотра заявки
    """
    requester = UserSerializer(read_only=True)
    executor = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('id', 'requester', 'created_at', 'updated_at', 'completed_at')


class TicketAssignSerializer(serializers.Serializer):
    """
    Сериализатор для назначения заявки исполнителю
    """
    executor_id = serializers.IntegerField(required=True)
    
    def validate_executor_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            executor = User.objects.get(id=value, role='EXECUTOR')
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Пользователь с ролью 'Исполнитель' не найден"
            )
        return value


class TicketExecuteSerializer(serializers.Serializer):
    """
    Сериализатор для выполнения заявки
    """
    comment = serializers.CharField(required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        instance.status = Ticket.Status.COMPLETED
        instance.completed_at = timezone.now()
        instance.save()
        return instance
