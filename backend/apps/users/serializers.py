"""
Сериализаторы для пользователей
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'role', 'phone', 'department')
        read_only_fields = ('id',)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Пароли не совпадают"}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения данных пользователя
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'role_display', 'phone', 'department', 'date_joined')
        read_only_fields = ('id', 'username', 'date_joined')


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для аутентификации пользователя
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
