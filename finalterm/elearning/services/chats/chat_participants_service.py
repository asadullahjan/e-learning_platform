from elearning.models import ChatParticipant, ChatRoom, User
from elearning.exceptions import ServiceError
from elearning.permissions.chats.chat_participant_permissions import (
    ChatParticipantPolicy,
)


class ChatParticipantsService:
    """Service for managing chat participants"""

    @staticmethod
    def add_user_to_chat_by_username(chat_room: ChatRoom, username: str):
        """Add a user to a chat room by username"""
        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            raise ServiceError.not_found(f"User '{username}' not found")

        # Check if user is already a participant
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user
        ).exists():
            raise ServiceError.conflict(
                f"User '{username}' is already a participant in this chat"
            )

        # Create new participant
        participant = ChatParticipant.objects.create(
            chat_room=chat_room, user=user, role="participant"
        )

        return participant

    @staticmethod
    def add_participants_to_chat(chat_room: ChatRoom, users: list[User]):
        """Add multiple users to a chat room"""
        participants = []
        for user in users:
            if not ChatParticipant.objects.filter(
                chat_room=chat_room, user=user
            ).exists():
                participant = ChatParticipant.objects.create(
                    chat_room=chat_room, user=user, role="participant"
                )
                participants.append(participant)

        return participants

    @staticmethod
    def remove_participant_from_chat(chat_room: ChatRoom, user: User):
        """Remove a participant from a chat room"""
        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=user
            )
            participant.delete()
            return True
        except ChatParticipant.DoesNotExist:
            return False

    @staticmethod
    def join_public_chat(chat_room: ChatRoom, user: User):
        """Join a public chat room"""
        # Check if user can join this chat
        ChatParticipantPolicy.check_can_join_chat(
            user, chat_room, raise_exception=True
        )

        # Check if already a participant
        participant, created = ChatParticipant.objects.get_or_create(
            chat_room=chat_room, user=user, defaults={"role": "participant"}
        )

        if not created and not participant.is_active:
            # Reactivate existing participant
            participant.is_active = True
            participant.save()

        return participant

    @staticmethod
    def leave_chat(chat_room: ChatRoom, user: User):
        """Leave a chat room (deactivate participation)"""
        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=user
            )
            participant.is_active = False
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            return False

    @staticmethod
    def update_participant_role(
        chat_room: ChatRoom, admin_user: User, target_user: User, new_role: str
    ):
        """Update a participant's role (admin only)"""
        # Check if admin user can update roles
        ChatParticipantPolicy.check_can_update_participant_role(
            admin_user, chat_room, raise_exception=True
        )

        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=target_user
            )
            participant.role = new_role
            participant.save()
            return participant
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                f"User '{target_user.username}' is not a participant "
                f"in this chat"
            )

    @staticmethod
    def deactivate_chat_for_user(chat_room: ChatRoom, user: User):
        """Deactivate a user's participation in a chat"""
        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=user
            )
            participant.is_active = False
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            return False

    @staticmethod
    def deactivate_participant_by_admin(
        chat_room: ChatRoom, admin_user: User, target_user: User
    ):
        """Deactivate a participant from a chat (admin only)"""
        # Check if admin user can deactivate participants
        ChatParticipantPolicy.check_can_remove_participant(
            admin_user, chat_room, raise_exception=True
        )
        
        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=target_user
            )
            participant.is_active = False
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                f"User '{target_user.username}' is not a participant "
                f"in this chat"
            )

    @staticmethod
    def reactivate_chat_for_user(chat_room: ChatRoom, user: User):
        """Reactivate a user's participation in a chat"""
        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=user
            )
            participant.is_active = True
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            # Create new participant if doesn't exist
            participant = ChatParticipant.objects.create(
                chat_room=chat_room, user=user, role="participant"
            )
            return True

    @staticmethod
    def get_chat_participants(chat_room: ChatRoom, is_active: bool = True):
        """Get all participants for a chat room"""
        return ChatParticipant.objects.filter(
            chat_room=chat_room, is_active=is_active
        ).select_related("user")

    @staticmethod
    def get_user_participant(chat_room: ChatRoom, user: User):
        """Get a specific user's participation in a chat room"""
        try:
            return ChatParticipant.objects.get(chat_room=chat_room, user=user)
        except ChatParticipant.DoesNotExist:
            return None

    @staticmethod
    def is_user_participant(chat_room: ChatRoom, user: User):
        """Check if a user is an active participant in a chat room"""
        return ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, is_active=True
        ).exists()

    @staticmethod
    def is_user_admin(chat_room: ChatRoom, user: User):
        """Check if a user is an admin of a chat room"""
        return ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, role="admin", is_active=True
        ).exists()
