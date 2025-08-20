from rest_framework import viewsets
from elearning.serializers.chats.chat_participant_serializers import (
    ChatParticipantListSerializer,
    ChatParticipantRoleUpdateSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from elearning.services.chats.chat_participants_service import (
    ChatParticipantsService,
)
from rest_framework import status
from elearning.models import User, ChatParticipant

from elearning.views.chats.permissions.chat_participant_permissions import (
    ChatParticipantPermissions,
)


class ChatParticipantViewSet(viewsets.ViewSet):
    """ViewSet for chat participant operations"""

    permission_classes = [ChatParticipantPermissions]

    def list(self, request, chat_room_id=None):
        """List all chat participants"""
        chat_participants = ChatParticipantsService.get_chat_participants(
            request.chat_room, is_active=True
        )
        serializer = ChatParticipantListSerializer(
            chat_participants, many=True
        )
        return Response(serializer.data)

    def create(self, request, chat_room_id=None):
        """Create a new chat participant (join a chat or add user)"""
        username = request.data.get("username")

        # If username is provided, admin is adding another user
        if username:
            try:
                user_to_add = User.objects.get(
                    username=username, is_active=True
                )

                # Check if user is already a participant
                if ChatParticipant.objects.filter(
                    chat_room=request.chat_room,
                    user=user_to_add,
                    is_active=True,
                ).exists():
                    return Response(
                        {
                            "error": "User is already a participant in this chat"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Add participant using existing method
                ChatParticipantsService.add_participants_to_chat(
                    request.chat_room, [user_to_add]
                )

                # Get the created participant for response
                participant = ChatParticipant.objects.get(
                    chat_room=request.chat_room, user=user_to_add
                )

                return Response(
                    {
                        "message": f"Successfully added {username} to "
                        f"{request.chat_room.name}",
                        "participant": ChatParticipantListSerializer(
                            participant
                        ).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except User.DoesNotExist:
                return Response(
                    {"error": f"User '{username}' not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Otherwise, user is joining the chat themselves
        participant = ChatParticipantsService.join_public_chat(
            request.chat_room, request.user
        )

        return Response(
            {
                "message": f"Successfully joined {request.chat_room.name}",
                "role": participant.role,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def update_role(self, request, chat_room_room_id=None):
        """Update a chat participant role (admin only)"""
        serializer = ChatParticipantRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ChatParticipantsService.update_participant_role(
            request.chat_room,
            request.user,  # Current user (admin)
            serializer.validated_data["user"],  # Target user (User object)
            serializer.validated_data["role"],
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
