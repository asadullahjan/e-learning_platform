from elearning.models import ChatParticipant, ChatRoom, User


class ChatUtils:

    @staticmethod
    def is_user_admin(chat_room: ChatRoom, user: User) -> bool:
        """Check if a user is an admin of a chat room"""
        return ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, role="admin"
        ).exists()
