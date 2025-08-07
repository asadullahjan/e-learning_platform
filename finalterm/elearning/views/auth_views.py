from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from ..serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
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
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        login(request, user)
        return Response(
            {"message": "Login successful", "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout endpoint"""
    # Always logout regardless of authentication status
    if request.user.is_authenticated:
        logout(request)
    return Response(
        {"message": "Logout successful"}, status=status.HTTP_200_OK
    )
