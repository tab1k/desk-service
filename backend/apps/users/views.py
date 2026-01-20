"""
Представления для пользователей
"""
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    LoginSerializer
)

User = get_user_model()


@extend_schema(
    summary="Регистрация пользователя",
    description="Регистрация нового пользователя в системе. Возвращает данные пользователя и JWT токены.",
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description="Пользователь успешно создан"
        ),
        400: OpenApiResponse(description="Ошибка валидации данных")
    }
)
class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Вход в систему (Login)",
    description="Аутентификация пользователя по username и password. Возвращает JWT токены (access/refresh).",
    responses={
        200: OpenApiResponse(description="Успешный вход, возвращаются токены и данные пользователя"),
        401: OpenApiResponse(description="Неверные учетные данные")
    }
)
class LoginView(generics.GenericAPIView):
    """
    Аутентификация пользователя и получение JWT токенов
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'detail': 'Неверные учетные данные'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


@extend_schema(
    summary="Профиль пользователя",
    description="Получение и частичное обновление данных текущего авторизованного пользователя.",
    responses={
        200: UserSerializer,
        401: OpenApiResponse(description="Не авторизован")
    }
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Получение и обновление профиля текущего пользователя
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

