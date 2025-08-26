from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from elearning.permissions import ChatRoomPermission
from ...serializers.chats.chat_room_serializers import (
    ChatRoomListSerializer,
    ChatRoomSerializer,
)
from ...services.chats.chat_service import ChatService


class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for chat room operations"""

    permission_classes = [ChatRoomPermission]

    def get_queryset(self):
        # Use the service for business logic with computed fields
        return ChatService.get_chats_with_computed_fields(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to populate computed fields for single chat"""
        # Get the chat from the queryset that has computed fields
        chat_id = kwargs.get('pk')
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

    def get_serializer_class(self):
        if self.action == "list":
            return ChatRoomListSerializer
        return ChatRoomSerializer

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
