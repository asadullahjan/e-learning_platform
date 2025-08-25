from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from elearning.serializers.chats.chat_participant_serializers import (
    ChatParticipantListSerializer,
    ChatParticipantRoleUpdateSerializer,
    ChatParticipantCreateSerializer,
)
from elearning.services.chats.chat_participants_service import (
    ChatParticipantsService,
)
from elearning.permissions import ChatParticipantPermission
from elearning.models import ChatParticipant


class ChatParticipantViewSet(viewsets.ModelViewSet):
    """ViewSet for chat participant operations"""

    permission_classes = [ChatParticipantPermission]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == "create":
            return ChatParticipantCreateSerializer
        elif self.action == "update_role":
            return ChatParticipantRoleUpdateSerializer
        return ChatParticipantListSerializer

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
        serializer = self.get_serializer(chat_participants, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Handle the actual creation logic"""
        username = serializer.validated_data.get("username")

        if username:
            # Admin is adding another user
            participant = ChatParticipantsService.add_user_to_chat_by_username(
                self.request.chat_room, username
            )
            # Store data for response customization
            self._creation_data = {
                "type": "add_user",
                "participant": participant,
                "username": username,
            }
        else:
            # User is joining the chat themselves
            participant = ChatParticipantsService.join_public_chat(
                self.request.chat_room, self.request.user
            )
            # Store data for response customization
            self._creation_data = {
                "type": "join_chat",
                "participant": participant,
            }

    def create(self, request, chat_room_pk=None):
        """Create a new chat participant (join a chat or add user)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Perform the creation
        self.perform_create(serializer)

        # Get creation data
        creation_data = getattr(self, "_creation_data", {})
        creation_type = creation_data.get("type")

        # Customize response based on action type
        if creation_type == "add_user":
            response = Response(
                {
                    "message": (
                        f"Successfully added {creation_data['username']} to "
                        f"{request.chat_room.name}"
                    ),
                    "participant": ChatParticipantListSerializer(
                        creation_data["participant"]
                    ).data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            response = Response(
                {
                    "message": (
                        f"Successfully joined {request.chat_room.name}"
                    ),
                    "role": creation_data["participant"].role,
                },
                status=status.HTTP_201_CREATED,
            )

        # Clean up instance attributes
        if hasattr(self, "_creation_data"):
            delattr(self, "_creation_data")

        return response

    @action(detail=False, methods=["post"])
    def update_role(self, request, chat_room_pk=None):
        """Update a chat participant role (admin only)"""
        serializer = self.get_serializer(data=request.data)
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

    def destroy(self, request, chat_room_pk=None, pk=None):
        """Remove a participant from chat (admin only)"""
        try:
            participant = ChatParticipant.objects.get(
                chat_room=request.chat_room, id=pk
            )
            ChatParticipantsService.remove_participant_from_chat(
                request.chat_room, participant.user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ChatParticipant.DoesNotExist:
            return Response(
                {"detail": "Participant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
