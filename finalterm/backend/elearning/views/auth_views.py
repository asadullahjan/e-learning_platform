from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    inline_serializer,
)
from rest_framework import serializers

from elearning.serializers.user_serializers import UserReadOnlySerializer

from elearning.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
)
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator


class AuthViewSet(viewsets.GenericViewSet):
    """ViewSet for authentication operations"""

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ["register", "login", "csrf_token"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == "register":
            return UserRegistrationSerializer
        elif self.action == "login":
            return UserLoginSerializer
        return UserReadOnlySerializer

    def get_serializer(self, *args, **kwargs):
        """Override to handle logout action without serializer"""
        if self.action == "logout":
            return None
        return super().get_serializer(*args, **kwargs)

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: inline_serializer(
                name="RegisterResponse",
                fields={
                    "message": serializers.CharField(
                        help_text="Success message"
                    ),
                    "user": UserReadOnlySerializer,
                },
            ),
            400: inline_serializer(
                name="RegisterError",
                fields={
                    "error": serializers.CharField(help_text="Error message")
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Success Response",
                value={
                    "message": "User registered successfully",
                    "user": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "role": "student",
                    },
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def register(self, request):
        """
        User registration endpoint

        Registers a new user with email and password.

        **Request Body:**
        - email: User's email address
        - password: User's password
        - username: User's username
        - role: User's role {STUDENT, TEACHER}

        **Response:**
        - 201: User registered successfully, returns user data
        - 400: Invalid data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(
            {
                "message": "User registered successfully",
                "user": UserReadOnlySerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: inline_serializer(
                name="LoginResponse",
                fields={
                    "message": serializers.CharField(
                        help_text="Success message"
                    ),
                    "user": UserReadOnlySerializer,
                },
            ),
            400: inline_serializer(
                name="LoginError",
                fields={
                    "error": serializers.CharField(help_text="Error message")
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Success Response",
                value={
                    "message": "Login successful",
                    "user": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "role": "student",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        """
        User login endpoint

        Authenticates a user with email and password.

        **Request Body:**
        - email: User's email address
        - password: User's password

        **Response:**
        - 200: Login successful, returns user data and token
        - 400: Invalid credentials
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response(
            {
                "message": "Login successful",
                "user": UserReadOnlySerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={
            200: inline_serializer(
                name="LogoutResponse",
                fields={
                    "message": serializers.CharField(
                        help_text="Success message"
                    )
                },
            )
        },
        examples=[
            OpenApiExample(
                "Success Response",
                value={"message": "Logout successful"},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def logout(self, request):
        """
        User logout endpoint

        Logs out the current user.

        **Response:**
        - 200: Logout successful, returns success message

        **Response Body:**
        ```json
        {
            "message": "Logout successful"
        }
        ```
        """
        logout(request)
        return Response(
            {"message": "Logout successful"}, status=status.HTTP_200_OK
        )

    @extend_schema(
        responses={
            200: inline_serializer(
                name="CSRFTokenResponse",
                fields={
                    "csrfToken": serializers.CharField(
                        help_text="CSRF token for form submissions"
                    ),
                    "sessionKey": serializers.CharField(
                        help_text="Session key"
                    ),
                    "message": serializers.CharField(
                        help_text="Success message"
                    ),
                },
            )
        },
        examples=[
            OpenApiExample(
                "Success Response",
                value={
                    "csrfToken": "abc123def456...",
                    "sessionKey": "xyz789uvw012...",
                    "message": "Cookies initialized successfully",
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @method_decorator(never_cache)
    @action(detail=False, methods=["get"])
    def csrf_token(self, request):
        """
        CSRF Token endpoint

        Initialize cookies and return CSRF token for frontend applications.
        This endpoint ensures both CSRF and session cookies are properly set.

        **Response:**
        - 200: Returns CSRF token and session information

        **Response Body:**
        ```json
        {
            "csrfToken": "string",
            "sessionKey": "string",
            "message": "Cookies initialized successfully"
        }
        ```
        """
        # Force session creation
        if not request.session.session_key:
            request.session.create()

        csrf_token = get_token(request)

        return Response(
            {
                "csrfToken": csrf_token,
                "sessionKey": request.session.session_key,
                "message": "Cookies initialized successfully",
            },
            status=status.HTTP_200_OK,
        )
