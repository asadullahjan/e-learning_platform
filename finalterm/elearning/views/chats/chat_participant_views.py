from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from elearning.serializers.chats.chat_participant_serializers import (
    ChatParticipantListSerializer,
    ChatParticipantRoleUpdateSerializer,
    ChatParticipantCreateSerializer,
)
from elearning.services.chats.chat_participants_service import (
    ChatParticipantsService,
)
from elearning.permissions import ChatParticipantPermission
from elearning.models import ChatParticipant


@extend_schema(
    tags=["Chat Participants"],
    parameters=[
        OpenApiParameter(
            name="chat_room_pk",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Chat room ID"
        ),
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Participant ID"
        ),
    ],
)
class ChatParticipantViewSet(viewsets.ModelViewSet):
    """ViewSet for chat participant operations"""

    permission_classes = [ChatParticipantPermission]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == "create":
            return ChatParticipantCreateSerializer
        elif self.action == "update_role":
            return ChatParticipantRoleUpdateSerializer
        return ChatParticipantListSerializer

    def get_queryset(self):
        """Return participants for the specific chat room"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return ChatParticipant.objects.none()
            
        chat_room_id = self.kwargs["chat_room_pk"]
        return ChatParticipant.objects.filter(
            chat_room_id=chat_room_id
        ).select_related("user")

    @extend_schema(
        responses={
            200: ChatParticipantListSerializer(many=True),
        },
    )
    def list(self, request, chat_room_pk=None):
        """List all chat participants"""
        chat_participants = ChatParticipantsService.get_chat_participants(
            request.chat_room, is_active=True
        )
        serializer = self.get_serializer(chat_participants, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Handle the actual creation logic"""
        username = serializer.validated_data.get("username")

        if username:
            # Admin is adding another user
            participant = ChatParticipantsService.add_user_to_chat_by_username(
                self.request.chat_room, username
            )
            # Store data for response customization
            self._creation_data = {
                "type": "add_user",
                "participant": participant,
                "username": username,
            }
        else:
            # User is joining the chat themselves
            participant = ChatParticipantsService.join_public_chat(
                self.request.chat_room, self.request.user
            )
            # Store data for response customization
            self._creation_data = {
                "type": "join_chat",
                "participant": participant,
            }

    @extend_schema(
        request=ChatParticipantCreateSerializer,
        responses={
            201: inline_serializer(
                name="ChatParticipantCreateResponse",
                fields={
                    "message": serializers.CharField(
                        help_text="Success message"
                    ),
                    "participant": ChatParticipantListSerializer,
                    "role": serializers.CharField(
                        help_text="User role in chat",
                        required=False
                    ),
                },
            ),
            400: inline_serializer(
                name="ChatParticipantCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(
                        help_text="Error message"
                    ),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Add User to Chat",
                value={"username": "john_doe"},
                request_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Join Chat",
                value={},
                request_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def create(self, request, chat_room_pk=None):
        """Create a new chat participant (join a chat or add user)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Perform the creation
        self.perform_create(serializer)

        # Get creation data
        creation_data = getattr(self, "_creation_data", {})
        creation_type = creation_data.get("type")

        # Customize response based on action type
        if creation_type == "add_user":
            response = Response(
                {
                    "message": (
                        f"Successfully added {creation_data['username']} to "
                        f"{request.chat_room.name}"
                    ),
                    "participant": ChatParticipantListSerializer(
                        creation_data["participant"]
                    ).data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            response = Response(
                {
                    "message": (
                        f"Successfully joined {request.chat_room.name}"
                    ),
                    "role": creation_data["participant"].role,
                },
                status=status.HTTP_201_CREATED,
            )

        # Clean up instance attributes
        if hasattr(self, "_creation_data"):
            delattr(self, "_creation_data")

        return response

    @extend_schema(
        request=ChatParticipantRoleUpdateSerializer,
        responses={
            200: ChatParticipantRoleUpdateSerializer,
            400: inline_serializer(
                name="ChatParticipantRoleUpdateBadRequestResponse",
                fields={
                    "error": serializers.CharField(
                        help_text="Error message"
                    ),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Update Role",
                value={
                    "user": 1,
                    "role": "admin"
                },
                request_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def update_role(self, request, chat_room_pk=None):
        """Update a chat participant role (admin only)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ChatParticipantsService.update_participant_role(
            request.chat_room,
            request.user,  # Current user (admin)
            serializer.validated_data["user"],  # Target user (User object)
            serializer.validated_data["role"],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: None,
        },
    )
    @action(detail=False, methods=["post"])
    def deactivate(self, request, chat_room_pk=None):
        """Deactivate a chat participant"""
        ChatParticipantsService.deactivate_chat_for_user(
            request.chat_room, request.user
        )
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: None,
        },
    )
    @action(detail=False, methods=["post"])
    def reactivate(self, request, chat_room_pk=None):
        """Reactivate a chat participant"""
        ChatParticipantsService.reactivate_chat_for_user(
            request.chat_room, request.user
        )
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            204: None,
            404: inline_serializer(
                name="ChatParticipantNotFoundResponse",
                fields={
                    "detail": serializers.CharField(
                        help_text="Error message"
                    ),
                },
            ),
        },
    )
    def destroy(self, request, chat_room_pk=None, pk=None):
        """Remove a participant from chat (admin only)"""
        try:
            participant = ChatParticipant.objects.get(
                chat_room=request.chat_room, id=pk
            )
            ChatParticipantsService.remove_participant_from_chat(
                request.chat_room, participant.user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ChatParticipant.DoesNotExist:
            return Response(
                {"detail": "Participant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
