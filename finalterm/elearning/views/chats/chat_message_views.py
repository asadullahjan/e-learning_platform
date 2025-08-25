from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from elearning.serializers.chats.chat_message_serializers import (
    ChatMessageCreateUpdateSerializer,
    ChatMessageSerializer,
)
from elearning.services.chats.chat_messages_service import ChatMessagesService
from elearning.permissions import ChatMessagePermission
from elearning.models import ChatMessage
from elearning.services.chats.chat_websocket_service import (
    ChatWebSocketService,
)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for chat messages with automatic pagination and filtering.
    Inherits from ModelViewSet to get all CRUD operations and pagination 
    for free.
    """

    serializer_class = ChatMessageSerializer
    permission_classes = [ChatMessagePermission]
    http_method_names = ["get", "post", "patch", "delete"]  # No PUT method

    def get_queryset(self):
        """
        Filter messages by chat room and order by creation date.
        This enables automatic pagination and filtering.
        """
        chat_room_id = self.kwargs["chat_room_pk"]
        return ChatMessage.objects.filter(chat_room_id=chat_room_id).order_by(
            "-created_at"
        )  # Newest first

    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        """
        if self.action in ["create", "partial_update"]:
            return ChatMessageCreateUpdateSerializer
        return ChatMessageSerializer

    def create(self, request, chat_room_pk=None):
        """
        Create a new message and broadcast via WebSocket.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_message = ChatMessagesService(chat_room_pk).create_message(
            request.user, serializer.validated_data["content"]
        )

        response_data = ChatMessageSerializer(created_message).data

        # Broadcast complete message data with event type
        ChatWebSocketService.broadcast_message(
            response_data, "message_created"
        )
        return Response(response_data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, chat_room_pk=None, pk=None):
        """
        Update a message and broadcast via WebSocket.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_message = ChatMessagesService(chat_room_pk).update_message(
            serializer.validated_data["content"], request.user, pk
        )

        response_data = ChatMessageSerializer(updated_message).data

        # Broadcast complete updated message data
        ChatWebSocketService.broadcast_message(
            response_data, "message_updated"
        )
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, chat_room_pk=None, pk=None):
        """
        Delete a message and broadcast via WebSocket.
        """
        # Get complete message data before deleting
        message = self.get_object()
        message_data = ChatMessageSerializer(message).data

        ChatMessagesService(chat_room_pk).delete_message(pk, request.user)

        # Broadcast complete message data with deletion flag
        ChatWebSocketService.broadcast_message(message_data, "message_deleted")
        return Response(status=status.HTTP_204_NO_CONTENT)
