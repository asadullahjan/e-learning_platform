from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from elearning.serializers.chats.chat_participant_serializers import (
    ChatParticipantListSerializer,
    ChatParticipantRoleUpdateSerializer,
)
from elearning.services.chats.chat_participants_service import (
    ChatParticipantsService,
)
from elearning.permissions import ChatParticipantPermission
from elearning.models import User, ChatParticipant


class ChatParticipantViewSet(viewsets.ModelViewSet):
    """ViewSet for chat participant operations"""

    permission_classes = [ChatParticipantPermission]
    serializer_class = ChatParticipantListSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        """Return participants for the specific chat room"""
        chat_room_id = self.kwargs["chat_room_pk"]
        return ChatParticipant.objects.filter(
            chat_room_id=chat_room_id
        ).select_related("user")

    def list(self, request, chat_room_pk=None):
        """List all chat participants"""
        chat_participants = ChatParticipantsService.get_chat_participants(
            request.chat_room, is_active=True
        )
        serializer = ChatParticipantListSerializer(
            chat_participants, many=True
        )
        return Response(serializer.data)

    def create(self, request, chat_room_pk=None):
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
                            "detail": (
                                "User is already a participant in this chat"
                            )
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
                    {"detail": f"User '{username}' not found"},
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
    def update_role(self, request, chat_room_pk=None):
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
    def deactivate(self, request, chat_room_pk=None):
        """Deactivate a chat participant"""
        ChatParticipantsService.deactivate_chat_for_user(
            request.chat_room, request.user
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def reactivate(self, request, chat_room_pk=None):
        """Reactivate a chat participant"""
        ChatParticipantsService.reactivate_chat_for_user(
            request.chat_room, request.user
        )
        return Response(status=status.HTTP_200_OK)
