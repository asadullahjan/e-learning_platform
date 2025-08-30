from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from elearning.serializers.chats import (
    ChatParticipantReadOnlySerializer,
    ChatParticipantWriteSerializer,
)
from elearning.services.chats import (
    ChatParticipantsService,
)
from elearning.permissions.chats import ChatParticipantPermission
from elearning.models import ChatParticipant, ChatRoom


@extend_schema(
    tags=["Chat Participants"],
    parameters=[
        OpenApiParameter(
            name="chat_room_pk",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Chat room ID",
        ),
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Participant ID",
        ),
    ],
)
class ChatParticipantViewSet(viewsets.ModelViewSet):
    """ViewSet for chat participant operations"""

    permission_classes = [ChatParticipantPermission]
    http_method_names = ["get", "post", "patch"]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action in [
            "create",
            "update_role",
            "deactivate",
            "reactivate",
        ]:
            return ChatParticipantWriteSerializer
        return ChatParticipantReadOnlySerializer

    def get_queryset(self):
        """Return participants for the specific chat room"""
        # Handle swagger schema generation
        if getattr(self, "swagger_fake_view", False):
            return ChatParticipant.objects.none()

        # Fetch and cache the chat room for reuse in actions
        self.chat_room = self.get_chat_room()

        # Check permissions and get participants via service
        # Service will raise ServiceError if permission denied,
        # which DRF handles
        participants = ChatParticipantsService.get_participants(
            self.chat_room, self.request.user
        )
        return participants

    def get_chat_room(self):
        """Get the chat room for the current request"""
        if hasattr(self, "chat_room") and self.chat_room:
            return self.chat_room

        chat_room_id = self.kwargs.get("chat_room_pk")

        # Let DRF handle the DoesNotExist exception
        self.chat_room = ChatRoom.objects.get(id=chat_room_id)
        return self.chat_room

    def perform_create(self, serializer):
        """Handle the actual creation logic"""
        chat_room = self.get_chat_room()

        user = serializer.validated_data.get("user")

        if user:
            # Admin is adding another user
            participant = ChatParticipantsService.add_participant_to_chat(
                chat_room, user, self.request.user
            )

        else:
            # User is joining the chat themselves
            participant = ChatParticipantsService.join_chat(
                chat_room, self.request.user
            )

        serializer.instance = participant

    @extend_schema(
        request=ChatParticipantWriteSerializer,
        responses={
            200: ChatParticipantReadOnlySerializer,
            400: inline_serializer(
                name="ChatParticipantRoleUpdateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Update Role",
                value={"user": 1, "role": "admin"},
                request_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def update_role(self, request, chat_room_pk=None):
        """Update a chat participant role (admin only)"""
        chat_room = self.get_chat_room()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ChatParticipantsService.update_participant_role(
            chat_room,
            request.user,  # Current user (admin)
            serializer.validated_data["user"],  # Target user
            serializer.validated_data["role"],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ChatParticipantWriteSerializer,
        responses={
            200: None,
        },
        examples=[
            OpenApiExample(
                "Deactivate Self",
                value={},
                request_only=True,
                status_codes=["200"],
                description=(
                    "User deactivates themselves (no user field needed)"
                ),
            ),
            OpenApiExample(
                "Admin Deactivates User",
                value={"user": 1},
                request_only=True,
                status_codes=["200"],
                description="Admin deactivates user with ID 1",
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def deactivate(self, request, chat_room_pk=None):
        """Deactivate a chat participant (admin can deactivate others)"""
        chat_room = self.get_chat_room()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If user specified, admin is deactivating someone else
        # If no user specified, user is deactivating themselves
        user = serializer.validated_data.get("user", request.user)

        ChatParticipantsService.deactivate_participant(
            chat_room, user, request.user
        )
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        request=ChatParticipantWriteSerializer,
        responses={
            200: None,
        },
        examples=[
            OpenApiExample(
                "Reactivate Self",
                value={},
                request_only=True,
                status_codes=["200"],
                description=(
                    "User reactivates themselves (no user field needed)"
                ),
            ),
            OpenApiExample(
                "Admin Reactivates User",
                value={"user": 1},
                request_only=True,
                status_codes=["200"],
                description="Admin reactivates user with ID 1",
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def reactivate(self, request, chat_room_pk=None):
        """Reactivate a chat participant (admin can reactivate others)"""
        chat_room = self.get_chat_room()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If user specified, admin is reactivating someone else
        # If no user specified, user is reactivating themselves
        user = serializer.validated_data.get("user", request.user)

        ChatParticipantsService.reactivate_participant(
            chat_room, user, request.user
        )
        return Response(status=status.HTTP_200_OK)
