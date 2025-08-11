from rest_framework import viewsets
from ...models import ChatRoom, ChatParticipant
from .permissions.chat_room_permissions import ChatRoomPermission
from ...serializers.chats.chat_room_serializers import (
    ChatRoomListSerializer,
    ChatRoomSerializer,
)


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for chat room operations"""

    queryset = ChatRoom.objects.all()
    permission_classes = [ChatRoomPermission]

    def get_queryset(self):
        return ChatRoom.objects.filter(participants__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return ChatRoomListSerializer
        return ChatRoomSerializer

    def perform_create(self, serializer):
        """Create chat room and add current user as admin"""
        chat_room = serializer.save(created_by=self.request.user)
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=self.request.user,
            role="admin",
        )
