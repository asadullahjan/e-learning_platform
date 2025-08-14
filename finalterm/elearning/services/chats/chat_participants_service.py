from elearning.models import ChatParticipant, ChatRoom
from elearning.exceptions import ServiceError
from django.contrib.auth.models import User

from elearning.services.chats.chat_utils import ChatUtils


class ChatParticipantsService:
    @staticmethod
    def get_chat_participants(chat_room: ChatRoom):
        """Get all participants of a chat room"""
        return ChatParticipant.objects.filter(chat_room=chat_room)

    @staticmethod
    def add_participants_to_chat(
        chat_room: ChatRoom,
        participants: list[User],
    ):
        """Add participants to a chat room and add creator as admin"""

        bulk_participants = [
            ChatParticipant(
                chat_room=chat_room,
                user=participant,
                role="participant",
            )
            for participant in participants
        ]

        ChatParticipant.objects.bulk_create(bulk_participants)

    @staticmethod
    def update_participant_role(
        chat_room: ChatRoom, user: User, participant: User, role: str
    ):
        """Update the role of a participant in a chat room"""

        if not ChatUtils.is_user_admin(chat_room, user):
            raise ServiceError.permission_denied(
                "User is not an admin of this chat room"
            )

        if user == participant:
            raise ServiceError.bad_request("Cannot change your own role")

        ChatParticipant.objects.filter(
            chat_room=chat_room, user=participant
        ).update(role=role)

    @staticmethod
    def deactivate_chat_for_user(chat_room, user):
        """Deactivate chat for specific user only"""
        if chat_room.chat_type != "direct":
            raise ServiceError.bad_request(
                "Only direct chats can be deactivated"
            )

        try:
            participant = chat_room.participants.get(user=user)
            participant.is_active = False
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                "User is not a participant in this chat"
            )

    @staticmethod
    def reactivate_chat_for_user(chat_room: ChatRoom, user: User):
        """Reactivate chat for specific user"""
        try:
            participant = chat_room.participants.get(user=user)
            participant.is_active = True
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                "User is not a participant in this chat"
            )
