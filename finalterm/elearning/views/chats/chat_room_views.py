from rest_framework import viewsets
from ...models import ChatRoom
from .permissions.chat_room_permissions import ChatRoomPermission
from ...serializers.chats.chat_room_serializers import (
    ChatRoomListSerializer,
    ChatRoomSerializer,
)
from ...services.chats.chat_service import ChatService
from django.db import models


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for chat room operations"""

    permission_classes = [ChatRoomPermission]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            # Anonymous users only see public chats
            return ChatRoom.objects.filter(is_public=True)

        # Authenticated users see:
        # 1. Public chats
        # 2. Private chats they participate in
        # 3. Course chats they teach
        return ChatRoom.objects.filter(
            models.Q(is_public=True)
            | models.Q(participants__user=user, participants__is_active=True)
            | models.Q(course__teacher=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return ChatRoomListSerializer
        return ChatRoomSerializer

    def perform_create(self, serializer):
        """Override create to handle existing direct chats"""
        # Create new chat
        chat_room = ChatService.create_chat_room(
            serializer.validated_data, self.request.user
        )

        serializer.instance = chat_room
