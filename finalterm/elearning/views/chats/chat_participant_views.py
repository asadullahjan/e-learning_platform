from rest_framework import viewsets
from elearning.serializers.chats.chat_participant_serializers import (
    ChatParticipantListSerializer,
    ChatParticipantCreateUpdateSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from elearning.services.chats.chat_participants_service import (
    ChatParticipantsService,
)
from rest_framework import status

from elearning.views.chats.permissions.chat_participant_permissions import (
    ChatParticipantPermissions,
)


class ChatParticipantViewSet(viewsets.ViewSet):
    """ViewSet for chat participant operations"""

    permission_classes = [ChatParticipantPermissions]

    @action(detail=False, methods=["get"])
    def list_chat_participants(self, request, chat_room_id=None):
        """List all chat participants"""
        chat_participants = ChatParticipantsService.get_chat_participants(
            request.chat_room
        )
        serializer = ChatParticipantListSerializer(
            chat_participants, many=True
        )
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def create_chat_participant(self, request, chat_room_id=None):
        """Create a new chat participant"""
        serializer = ChatParticipantCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ChatParticipantsService.add_participants_to_chat(
            request.chat_room, [serializer.validated_data["user"]]
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def update_role(self, request, chat_room_id=None):
        """Update a chat participant"""
        serializer = ChatParticipantCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ChatParticipantsService.update_participant_role(
            request.chat_room,
            request.user,
            request.data["user"],
            request.data["role"],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def deactivate(self, request, chat_room_id=None):
        """Deactivate a chat participant"""
        ChatParticipantsService.deactivate_chat_for_user(
            request.chat_room, request.user
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def reactivate(self, request, chat_room_id=None):
        """Reactivate a chat participant"""
        ChatParticipantsService.reactivate_chat_for_user(
            request.chat_room, request.user
        )
        return Response(status=status.HTTP_200_OK)
