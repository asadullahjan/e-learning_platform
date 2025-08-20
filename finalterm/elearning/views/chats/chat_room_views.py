from rest_framework import viewsets, status
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

    @action(detail=False, methods=["post"])
    def find_or_create_direct(self, request):
        """Find existing direct chat or create new one with another user"""

        username = request.data.get("username")
        if not username:
            return Response(
                {"error": "Username is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            chat_room, created = ChatService.find_or_create_direct_chat(
                request.user, username
            )
            serializer = self.get_serializer(chat_room)
            return Response(
                {"chat_room": serializer.data, "created": created},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(f"Error in find_or_create_direct: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """Override create to handle existing direct chats"""
        # Create new chat
        chat_room = ChatService.create_chat_room(
            serializer.validated_data, self.request.user
        )

        serializer.instance = chat_room
