from rest_framework import viewsets, status
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
from elearning.permissions import ChatRoomPermission
from ...serializers.chats.chat_room_serializers import (
    ChatRoomListSerializer,
    ChatRoomSerializer,
)
from ...services.chats.chat_service import ChatService


@extend_schema(
    tags=["Chat Rooms"],
)
class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for chat room operations"""

    permission_classes = [ChatRoomPermission]

    def get_queryset(self):
        # Use the service for business logic with computed fields
        return ChatService.get_chats_with_computed_fields(self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ChatRoomListSerializer
        return ChatRoomSerializer

    @extend_schema(
        responses={
            200: ChatRoomListSerializer(many=True),
        },
        description=(
            "List all chat rooms accessible to the current user "
            "(public chats + user's private chats)"
        ),
        summary="List accessible chat rooms",
    )
    def list(self, request, *args, **kwargs):
        """List all accessible chat rooms for the current user"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Chat room ID",
            ),
        ],
        responses={
            200: ChatRoomSerializer,
            404: inline_serializer(
                name="ChatRoomNotFoundResponse",
                fields={
                    "detail": serializers.CharField(help_text="Error message"),
                },
            ),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to populate computed fields for single chat"""
        # Get the chat from the queryset that has computed fields
        chat_id = kwargs.get("pk")
        try:
            instance = ChatService.get_chat_with_permission_check(
                int(chat_id), request.user
            )
            # Populate computed fields before serialization
            instance = ChatService.populate_chat_computed_fields(
                instance, request.user
            )
        except Exception:
            # Fall back to default behavior if service fails
            instance = self.get_object()
            instance = ChatService.populate_chat_computed_fields(
                instance, request.user
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        responses={
            200: ChatRoomListSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"])
    def my_chats(self, request):
        """Get only the chats where the user is a participant"""
        # Get user chats and populate computed fields
        user_chats = ChatService.get_user_chats(request.user)

        # Populate computed fields for each chat
        chats_with_fields = []
        for chat in user_chats:
            chat_with_fields = ChatService.populate_chat_computed_fields(
                chat, request.user
            )
            chats_with_fields.append(chat_with_fields)

        # Let Django handle serializer creation and context automatically
        serializer = self.get_serializer(chats_with_fields, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=inline_serializer(
            name="FindOrCreateDirectRequest",
            fields={
                "username": serializers.CharField(
                    help_text="Username to find or create direct chat with"
                ),
            },
        ),
        responses={
            200: inline_serializer(
                name="FindOrCreateDirectResponse",
                fields={
                    "chat_room": ChatRoomSerializer,
                    "created": serializers.BooleanField(
                        help_text="Whether a new chat was created"
                    ),
                },
            ),
            400: inline_serializer(
                name="FindOrCreateDirectBadRequestResponse",
                fields={
                    "detail": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Find or Create Direct Chat",
                value={"username": "john_doe"},
                request_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def find_or_create_direct(self, request):
        """Find existing direct chat or create new one with another user"""

        username = request.data.get("username")
        if not username:
            return Response(
                {"detail": "Username is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            chat_room, created = ChatService.find_or_create_direct_chat(
                request.user, username
            )
            # Populate computed fields before serialization
            chat_room = ChatService.populate_chat_computed_fields(
                chat_room, request.user
            )
            serializer = self.get_serializer(chat_room)
            return Response(
                {"chat_room": serializer.data, "created": created},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        request=ChatRoomSerializer,
        responses={
            201: ChatRoomSerializer,
            400: inline_serializer(
                name="ChatRoomCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Create Chat Room",
                value={
                    "name": "Course Discussion",
                    "chat_type": "course",
                    "is_public": True,
                    "participants": [1, 2, 3],
                },
                request_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def perform_create(self, serializer):
        """Override create to handle existing direct chats"""
        # Create new chat
        chat_room = ChatService.create_chat_room(
            serializer.validated_data, self.request.user
        )

        # Populate computed fields before setting instance
        chat_room = ChatService.populate_chat_computed_fields(
            chat_room, self.request.user
        )
        serializer.instance = chat_room
