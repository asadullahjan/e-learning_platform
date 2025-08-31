from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from elearning.permissions import IsUserAuthenticatedAndOwner

from elearning.models import User
from elearning.serializers import (
    UserDetailReadOnlySerializer,
    UserUpdateSerializer,
)
from elearning.services.user_service import UserService


@extend_schema(
    tags=["Users"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Username",
        ),
    ],
)
class UserViewSet(ModelViewSet):
    """
    ViewSet for user operations with automatic pagination and search

    Users can view all users, view their own profile, update their profile,
    and retrieve other users by username.

    **Actions:**
    - list: View all users
    - retrieve: View a specific user
    - me: View current user profile
    - profile_update: Update current user profile
    """

    permission_classes = [IsUserAuthenticatedAndOwner]
    filter_backends = [SearchFilter]
    search_fields = ["username", "first_name", "last_name"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "me"]:
            return UserDetailReadOnlySerializer
        return UserUpdateSerializer

    def get_queryset(self):
        """Get queryset based on action"""
        if self.action in ["retrieve", "me"]:
            # For individual user retrieval, use computed fields
            return UserService.get_users_with_computed_fields()
        else:
            # For list, use basic queryset
            return User.objects.filter(is_active=True).order_by("username")

    @extend_schema(
        responses={
            200: UserDetailReadOnlySerializer,
        },
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Get current user profile - convenience endpoint

        Returns the current user's profile information.

        **Response:**
        - 200: User profile retrieved successfully
        """
        # Populate computed fields for current user
        user = UserService.populate_user_computed_fields(request.user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(
        request=UserUpdateSerializer,
        responses={
            200: UserDetailReadOnlySerializer,
            400: inline_serializer(
                name="UserProfileUpdateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Update Profile",
                value={
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                },
                request_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(detail=False, methods=["patch"])
    def profile_update(self, request):
        """
        Update current user profile

        Updates the current user's profile information.

        **Request Body:**
        - username: User's username (optional)
        - first_name: User's first name (optional)
        - last_name: User's last name (optional)
        - email: User's email address (optional)

        **Response:**
        - 200: User profile updated successfully
        - 400: Invalid data
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        return Response(UserDetailReadOnlySerializer(updated_user).data)

    @extend_schema(
        responses={
            200: UserDetailReadOnlySerializer,
            404: inline_serializer(
                name="UserNotFoundResponse",
                fields={
                    "detail": serializers.CharField(help_text="Error message"),
                },
            ),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get user by username (custom lookup)

        Returns a user's profile information by their username.

        **Response:**
        - 200: User profile retrieved successfully
        - 404: User not found
        """
        username = kwargs.get("pk")
        user = UserService.get_user_by_username(username)

        # Populate computed fields before serialization
        user = UserService.populate_user_computed_fields(user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
