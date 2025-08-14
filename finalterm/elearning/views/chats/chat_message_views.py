from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from elearning.serializers.chats.chat_message_serializers import (
    ChatMessageCreateUpdateSerializer,
)
from elearning.services.chats.chat_messages_service import ChatMessagesService
from elearning.views.chats.permissions.chat_message_permissions import (
    ChatMessagePermission,
)
from elearning.serializers.chats.chat_message_serializers import (
    ChatMessageSerializer,
)
from elearning.models import ChatMessage
from elearning.services.chats.chat_websocket_service import (
    ChatWebSocketService,
)


class ChatMessageViewSet(viewsets.GenericViewSet):
    permission_classes = [ChatMessagePermission]

    def list(self, request, chat_room_id=None):
        messages = ChatMessage.objects.filter(chat_room_id=chat_room_id)

        # Apply pagination properly
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = ChatMessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback if pagination is disabled
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, chat_room_id=None):
        serializer = ChatMessageCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_message = ChatMessagesService(chat_room_id).create_message(
            serializer.validated_data["content"], request.user
        )

        response_data = ChatMessageSerializer(created_message).data

        # Broadcast complete message data with event type
        ChatWebSocketService.broadcast_message(
            response_data, "message_created"
        )
        return Response(response_data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, chat_room_id=None, pk=None):
        serializer = ChatMessageCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_message = ChatMessagesService(chat_room_id).update_message(
            serializer.validated_data["content"], request.user, pk
        )

        response_data = ChatMessageSerializer(updated_message).data

        # Broadcast complete updated message data
        ChatWebSocketService.broadcast_message(
            response_data, "message_updated"
        )
        return Response(response_data, status=status.HTTP_200_OK)

    def destroy(self, request, chat_room_id=None, pk=None):
        # Get complete message data before deleting
        message = ChatMessage.objects.get(id=pk)
        message_data = ChatMessageSerializer(message).data

        ChatMessagesService(chat_room_id).delete_message(pk, request.user)

        # Broadcast complete message data with deletion flag
        ChatWebSocketService.broadcast_message(message_data, "message_deleted")
        return Response(status=status.HTTP_204_NO_CONTENT)
