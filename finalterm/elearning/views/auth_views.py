from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from ..serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
)


class AuthViewSet(viewsets.ViewSet):
    """ViewSet for authentication operations"""
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['register', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """User registration endpoint"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response(
                {
                    "message": "User registered successfully",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login endpoint"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return Response(
                {
                    "message": "Login successful", 
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """User logout endpoint"""
        # Always logout regardless of authentication status
        if request.user.is_authenticated:
            logout(request)
        return Response(
            {"message": "Logout successful"}, 
            status=status.HTTP_200_OK
        )
