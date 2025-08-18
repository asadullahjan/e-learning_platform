from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions.chat_room_permissions import ChatRoomPermission
from ...serializers.chats.chat_room_serializers import (
    ChatRoomListSerializer,
    ChatRoomSerializer,
)
from ...services.chats.chat_service import ChatService


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for chat room operations"""

    permission_classes = [ChatRoomPermission]

    def get_queryset(self):
        # Use the service for business logic
        return ChatService.get_all_available_chats(self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ChatRoomListSerializer
        return ChatRoomSerializer

    @action(detail=False, methods=["get"])
    def my_chats(self, request):
        """Get only the chats where the user is a participant"""
        # Use the service for business logic
        user_chats = ChatService.get_user_chats(request.user)

        # Let Django handle serializer creation and context automatically
        serializer = self.get_serializer(user_chats, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Override create to handle existing direct chats"""
        # Create new chat
        chat_room = ChatService.create_chat_room(
            serializer.validated_data, self.request.user
        )

        serializer.instance = chat_room
