"""
Представления для заявок
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import Ticket
from .serializers import (
    TicketCreateSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
    TicketAssignSerializer,
    TicketExecuteSerializer
)
from apps.users.permissions import IsRequester, IsOperator, IsExecutor

User = get_user_model()


@extend_schema(tags=['Заявки'])
class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заявками с различными правами доступа
    """
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['list', 'my_tickets', 'all_tickets', 'assigned_to_me']:
            return TicketListSerializer
        elif self.action == 'assign':
            return TicketAssignSerializer
        elif self.action == 'execute':
            return TicketExecuteSerializer
        return TicketDetailSerializer
    
    def get_permissions(self):
        """
        Определяем права доступа для разных действий
        """
        if self.action == 'create':
            # Создавать заявки могут только заявители
            permission_classes = [IsAuthenticated, IsRequester]
        elif self.action in ['all_tickets', 'assign', 'destroy']:
            # Просматривать все заявки и назначать могут только операторы
            permission_classes = [IsAuthenticated, IsOperator]
        elif self.action in ['assigned_to_me', 'execute']:
            # Просматривать назначенные заявки могут только исполнители
            permission_classes = [IsAuthenticated, IsExecutor]
        elif self.action == 'my_tickets':
            # Свои заявки могут просматривать только заявители
            permission_classes = [IsAuthenticated, IsRequester]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="Создание заявки",
        description="Создание новой заявки. Доступно только для роли **Заявитель (REQUESTER)**.",
        responses={201: TicketDetailSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Список заявок (Общий)",
        description="Возвращает список заявок (поведение зависит от роли, стандартный метод DRF).",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Детальная информация о заявке",
        description="Получение полной информации о заявке по ID.",
        responses={200: TicketDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Мои заявки",
        description="Список заявок, созданных текущим пользователем. Доступно только для роли **Заявитель (REQUESTER)**.",
        responses={200: TicketListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='my-tickets')
    def my_tickets(self, request):
        """
        Просмотр заявок, созданных текущим пользователем (заявитель)
        """
        tickets = Ticket.objects.filter(requester=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Все заявки",
        description="Список абсолютно всех заявок в системе. Доступно только для роли **Оператор (OPERATOR)**.",
        responses={200: TicketListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='all-tickets')
    def all_tickets(self, request):
        """
        Просмотр всех заявок (оператор)
        """
        tickets = Ticket.objects.all()
        page = self.paginate_queryset(tickets)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Назначенные мне",
        description="Список заявок, назначенных текущему исполнителю. Доступно только для роли **Исполнитель (EXECUTOR)**.",
        responses={200: TicketListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        """
        Просмотр заявок, назначенных текущему пользователю (исполнитель)
        """
        tickets = Ticket.objects.filter(executor=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Назначить исполнителя",
        description="Назначить исполнителя на заявку. Доступно только для роли **Оператор (OPERATOR)**.",
        request=TicketAssignSerializer,
        responses={
            200: TicketDetailSerializer,
            400: OpenApiResponse(description="Не указан ID исполнителя или исполнитель не найден")
        }
    )
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Назначение заявки исполнителю (оператор)
        """
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        executor_id = serializer.validated_data['executor_id']
        executor = User.objects.get(id=executor_id)
        
        ticket.executor = executor
        ticket.status = Ticket.Status.ASSIGNED
        ticket.save()
        
        return Response(
            TicketDetailSerializer(ticket).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Выполнить заявку",
        description="Завершить выполнение заявки, добавив комментарий. Доступно только для роли **Исполнитель (EXECUTOR)**.",
        request=TicketExecuteSerializer,
        responses={
            200: TicketDetailSerializer,
            403: OpenApiResponse(description="Заявка не назначена этому исполнителю")
        }
    )
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Выполнение заявки (исполнитель)
        """
        ticket = self.get_object()
        
        # Проверяем, что заявка назначена текущему пользователю
        if ticket.executor != request.user:
            return Response(
                {'detail': 'Эта заявка не назначена вам'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(ticket, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            TicketDetailSerializer(ticket).data,
            status=status.HTTP_200_OK
        )

