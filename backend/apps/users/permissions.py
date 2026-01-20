"""
Права доступа на основе ролей пользователей
"""
from rest_framework import permissions


class IsRequester(permissions.BasePermission):
    """
    Разрешение только для заявителей
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'REQUESTER'
        )


class IsOperator(permissions.BasePermission):
    """
    Разрешение только для операторов
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'OPERATOR'
        )


class IsExecutor(permissions.BasePermission):
    """
    Разрешение только для исполнителей
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'EXECUTOR'
        )


class IsRequesterOrOperator(permissions.BasePermission):
    """
    Разрешение для заявителей или операторов
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['REQUESTER', 'OPERATOR']
        )
