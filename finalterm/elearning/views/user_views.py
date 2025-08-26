from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import User
from ..serializers.user_serializers import UserSerializer, UserDetailSerializer
from ..services.user_service import UserService


class UserViewSet(ModelViewSet):
    """ViewSet for user operations with automatic pagination and search"""

    queryset = User.objects.filter(is_active=True).order_by("username")
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["username", "first_name", "last_name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        return UserSerializer

    def get_queryset(self):
        """Get queryset based on action"""
        if self.action == "retrieve":
            # For individual user retrieval, use computed fields
            return UserService.get_users_with_computed_fields()
        else:
            # For list, use basic queryset
            return User.objects.filter(is_active=True).order_by("username")

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user profile - convenience endpoint"""
        # Populate computed fields for current user
        user = UserService.populate_user_computed_fields(request.user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def profile(self, request):
        """Get current user profile - alias for me"""
        return self.me(request)

    @action(detail=False, methods=["patch"])
    def profile_update(self, request):
        """Update current user profile"""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Get user by username (custom lookup)"""
        # ✅ CORRECT: Delegate to service - ServiceError handled automatically
        username = kwargs.get("pk")
        user = UserService.get_user_by_username(username)
        
        # Populate computed fields before serialization
        user = UserService.populate_user_computed_fields(user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
