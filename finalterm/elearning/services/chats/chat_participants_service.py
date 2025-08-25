from elearning.models import ChatParticipant, ChatRoom, User
from elearning.exceptions import ServiceError
from elearning.services.notification_service import NotificationService

from elearning.services.chats.chat_utils import ChatUtils


class ChatParticipantsService:
    @staticmethod
    def get_chat_participants(
        chat_room: ChatRoom, is_active: bool = None
    ):
        """Get all participants of a chat room, optionally filtered by active 
        status"""
        queryset = ChatParticipant.objects.filter(chat_room=chat_room)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset

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

        # Notify participants about being added to group/course chat
        if chat_room.chat_type in ["group", "course"]:
            participant_user_ids = [p.id for p in participants]
            message = (
                f"You have been added to '{chat_room.name}' "
                f"by {chat_room.created_by.username}"
            )
            NotificationService.create_notifications_and_send(
                user_ids=participant_user_ids,
                title=f"Added to {chat_room.chat_type.title()} Chat",
                message=message,
                action_url=f"/chats/{chat_room.id}",
            )

    @staticmethod
    def add_user_to_chat_by_username(chat_room: ChatRoom, username: str):
        """Add a user to chat by username (admin only)"""
        try:
            user_to_add = User.objects.get(username=username, is_active=True)
            
            # Check if user is already a participant
            if ChatParticipant.objects.filter(
                chat_room=chat_room,
                user=user_to_add,
                is_active=True,
            ).exists():
                raise ServiceError.bad_request(
                    "User is already a participant in this chat"
                )

            # Add participant
            ChatParticipantsService.add_participants_to_chat(
                chat_room, [user_to_add]
            )

            # Return the created participant
            return ChatParticipant.objects.get(
                chat_room=chat_room, user=user_to_add
            )
        except User.DoesNotExist:
            raise ServiceError.not_found(f"User '{username}' not found")

    @staticmethod
    def remove_participant_from_chat(chat_room: ChatRoom, user: User):
        """Remove a participant from chat (admin only)"""
        if not ChatUtils.is_user_admin(chat_room, user):
            raise ServiceError.permission_denied(
                "User is not an admin of this chat room"
            )
        
        participant = ChatParticipant.objects.get(
            chat_room=chat_room, user=user
        )
        participant.delete()
        return participant

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

            # Notify user about chat access being restored
            if chat_room.chat_type in ["group", "course"]:
                message = (
                    f"Your access to '{chat_room.name}' has been restored "
                    f"by {chat_room.created_by.username}"
                )
                NotificationService.create_notifications_and_send(
                    user_ids=[user.id],
                    title="Chat Access Restored",
                    message=message,
                    action_url=f"/chats/{chat_room.id}",
                )

            return True
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                "User is not a participant in this chat"
            )
