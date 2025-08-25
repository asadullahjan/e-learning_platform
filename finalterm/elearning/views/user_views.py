from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import User
from ..serializers.user_serializers import UserSerializer


class UserViewSet(ModelViewSet):
    """ViewSet for user operations with automatic pagination and search"""

    queryset = User.objects.filter(is_active=True).order_by("username")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["username", "first_name", "last_name"]

    def get_queryset(self):
        """Get queryset based on action"""
        if self.action == "retrieve":
            # For individual user retrieval, allow inactive users
            return User.objects.all()
        return User.objects.filter(is_active=True).order_by("username")

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile - convenience endpoint"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get user by username (custom lookup)"""
        username = kwargs.get("pk")
        try:
            user = get_object_or_404(User, username=username)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            error_status = status.HTTP_404_NOT_FOUND
            return Response({"error": "User not found"}, status=error_status)
