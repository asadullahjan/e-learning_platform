from elearning.models import ChatParticipant, ChatRoom, User
from elearning.exceptions import ServiceError

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
    def join_public_chat(chat_room: ChatRoom, user: User):
        """Allow user to join a public chat room"""
        # Check if chat is public
        if not chat_room.is_public:
            raise ServiceError.permission_denied(
                "Cannot join private chat rooms"
            )

        # Check if user is already a participant
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, is_active=True
        ).exists():
            raise ServiceError.bad_request(
                "User is already a participant in this chat"
            )

        # Create participant with default role (always 'participant')
        participant = ChatParticipant.objects.create(
            chat_room=chat_room,
            user=user,
            role="participant",
            is_active=True,
        )

        return participant

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
    def promote_participant_to_admin(
        chat_room: ChatRoom, admin_user: User, participant_user: User
    ):
        """Promote a participant to admin role - admin only operation"""
        # Business logic: Only admins can promote others
        if not ChatUtils.is_user_admin(chat_room, admin_user):
            raise ServiceError.permission_denied(
                "Only admins can promote participants"
            )

        # Business logic: Cannot promote yourself
        if admin_user == participant_user:
            raise ServiceError.bad_request("Cannot promote yourself to admin")

        # Business logic: Update the role
        participant = ChatParticipant.objects.get(
            chat_room=chat_room, user=participant_user
        )
        participant.role = "admin"
        participant.save()

        return participant

    @staticmethod
    def demote_admin_to_participant(
        chat_room: ChatRoom, admin_user: User, target_user: User
    ):
        """Demote an admin to participant role - admin only operation"""
        # Business logic: Only admins can demote others
        if not ChatUtils.is_user_admin(chat_room, admin_user):
            raise ServiceError.permission_denied(
                "Only admins can demote participants"
            )

        # Business logic: Cannot demote yourself
        if admin_user == target_user:
            raise ServiceError.bad_request("Cannot demote yourself")

        # Business logic: Update the role
        participant = ChatParticipant.objects.get(
            chat_room=chat_room, user=target_user
        )
        participant.role = "participant"
        participant.save()

        return participant

    @staticmethod
    def deactivate_chat_for_user(chat_room, user):
        """Deactivate chat for specific user - works for all chat types"""
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
