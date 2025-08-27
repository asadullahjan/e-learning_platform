from rest_framework.permissions import BasePermission
from elearning.models import ChatRoom, ChatParticipant, User, Course
from elearning.exceptions import ServiceError


class ChatRoomPermission(BasePermission):
    """DRF permission class for chat room operations - basic checks only"""

    def has_permission(self, request, view):
        """Basic permission checks without database queries"""

        # For list/retrieve actions, allow all users
        # (service layer handles public vs private chat access)
        if view.action in ["list", "retrieve"]:
            return True

        # For all other actions, require authentication
        # (detailed permission checks happen in service layer)
        return request.user.is_authenticated


class ChatPolicy:
    """
    Policy class for chat operations.

    This class encapsulates all business rules for chat operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_create_chat_room(
        user: User,
        chat_type: str,
        course: Course = None,
        raise_exception=False,
    ) -> bool:
        """Check if a user can create a chat room"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to create chat rooms"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if chat_type == "course":
            if user.role != "teacher":
                error_msg = "Only teachers can create course chat rooms"
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                return False

            if course and course.teacher != user:
                error_msg = (
                    "You can only create chat rooms for courses you teach"
                )
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                return False

        return True

    @staticmethod
    def check_can_access_chat_room(
        user: User,
        chat_room: ChatRoom,
        raise_exception=False,
    ) -> bool:
        """Check if a user can access a chat room"""
        # Public chats: accessible to everyone
        if chat_room.is_public:
            return True

        # For private chats, user must be authenticated
        if not user.is_authenticated:
            error_msg = "You must be logged in to access private chat rooms"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Private chats: only accessible to participants
        if chat_room.participants.filter(user=user, is_active=True).exists():
            return True

        # Course chats: accessible to course teacher
        if chat_room.course and chat_room.course.teacher == user:
            return True

        error_msg = "You do not have access to this chat room"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_modify_chat_room(
        user: User,
        chat_room: ChatRoom,
        raise_exception=False,
    ) -> bool:
        """Check if a user can modify a chat room"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify chat rooms"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Only creator can modify
        if chat_room.created_by != user:
            error_msg = "Only the creator can modify this chat room"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_manage_participants(
        user: User,
        chat_room: ChatRoom,
        raise_exception=False,
    ) -> bool:
        """Check if a user can manage participants in a chat room"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to manage participants"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Only admins can manage participants
        try:
            participant = chat_room.participants.get(user=user)
            if participant.role != "admin":
                error_msg = "Only admins can manage participants"
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                return False
            return True
        except ChatParticipant.DoesNotExist:
            error_msg = "You must be a participant to manage this chat room"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False
