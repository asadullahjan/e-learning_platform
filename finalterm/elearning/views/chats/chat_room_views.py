from rest_framework import viewsets
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
from elearning.permissions.chats import ChatRoomPermission
from elearning.models import ChatRoom
from elearning.serializers.chats import (
    ChatRoomReadOnlySerializer,
    ChatRoomWriteSerializer,
    ChatRoomDetailReadOnlySerializer,
)
from elearning.services.chats.chat_service import ChatService


@extend_schema(
    tags=["Chat Rooms"],
)
class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for chat room operations"""

    permission_classes = [ChatRoomPermission]

    def get_queryset(self):
        # For list actions, filter by permissions
        if self.action == "list":
            return ChatService.get_chat_rooms(self.request.user)
        # For detail actions (retrieve, update, delete), get all chat rooms
        # Permission checks will be done in service layer to return proper 403
        return ChatRoom.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ChatRoomReadOnlySerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ChatRoomWriteSerializer
        return ChatRoomDetailReadOnlySerializer

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
            200: ChatRoomReadOnlySerializer,
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
        chat_id = kwargs.get("pk")
        instance = ChatService.get_chat_with_permission_check(
            int(chat_id), request.user
        )
        # Populate computed fields before serialization
        instance = ChatService.populate_chat_computed_fields(
            instance, request.user
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        responses={
            200: ChatRoomReadOnlySerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"])
    def my_chats(self, request):
        """Get only the chats where the user is a participant"""
        # Get user chats and populate computed fields
        user_chats = ChatService.get_user_chats(request.user)

        # Let Django handle serializer creation and context automatically
        serializer = self.get_serializer(user_chats, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ChatRoomWriteSerializer,
        responses={
            201: ChatRoomReadOnlySerializer,
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

        serializer.instance = chat_room

    def perform_update(self, serializer):
        """Override update to use service layer for permission checks"""
        instance = serializer.instance
        ChatService.update_chat_room(
            instance, self.request.user, **serializer.validated_data
        )

        serializer.instance = instance

    def perform_destroy(self, instance):
        """Override destroy to use service layer for permission checks"""
        ChatService.delete_chat_room(instance, self.request.user)
