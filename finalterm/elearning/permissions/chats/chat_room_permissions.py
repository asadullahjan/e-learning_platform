from rest_framework.permissions import BasePermission
from elearning.models import ChatRoom, ChatParticipant, User, Course
from elearning.exceptions import ServiceError


class ChatRoomPermission(BasePermission):
    """Handles permissions for ChatRoom operations"""

    def has_permission(self, request, view):
        # Handle list/retrieve actions first
        if view.action in ["list", "retrieve"]:
            return True  # Anyone can list/retrieve

        # Check authentication for other actions
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access chat rooms"
            return False

        # Handle create action and custom actions
        if view.action in ["create", "find_or_create_direct"]:
            # For find_or_create_direct, just check authentication
            if view.action == "find_or_create_direct":
                return True

            # For regular create, check chat type and course
            chat_type = request.data.get("chat_type")
            course = request.data.get("course")

            if chat_type == "course":
                # Only teachers can create course chatrooms
                if request.user.role != "teacher":
                    self.message = "Only teachers can create course chat rooms"
                    return False
                # Course must exist and user must be the teacher
                if (
                    course
                    and not request.user.courses_taught.filter(
                        id=course
                    ).exists()
                ):
                    self.message = (
                        "You can only create chat rooms for courses you teach"
                    )
                    return False

            return True  # Allow creation for other chat types

        # Also check for the URL path version
        if hasattr(view, "action") and view.action is None:
            # This might be a custom action that's not being recognized
            if request.path.endswith("find-or-create-direct/"):
                return True

        # Default to allowing other actions
        # (object permissions will handle them)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Handle retrieve action (individual chat access)
        if view.action == "retrieve":
            # Public chats: accessible to everyone
            if obj.is_public:
                return True

            # Private chats: only accessible to participants
            if obj.participants.filter(user=user, is_active=True).exists():
                return True

            # Course chats: accessible to course teacher
            if obj.course and obj.course.teacher == user:
                return True

            self.message = "You do not have access to this chat room"
            return False

        # Handle update/destroy actions
        if view.action in ["update", "partial_update", "destroy"]:
            # Only creator can modify
            if obj.created_by != user:
                self.message = "Only the creator can modify this chat room"
                return False
            return True

        # Handle custom actions
        if view.action in ["add_participants", "change_participant_role"]:
            # Only admins can manage participants
            try:
                participant = obj.participants.get(user=user)
                if participant.role != "admin":
                    self.message = "Only admins can manage participants"
                    return False
                return True
            except ChatParticipant.DoesNotExist:
                self.message = (
                    "You must be a participant to manage this chat room"
                )
                return False

        return obj.created_by == user  # For now only creator can modify


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
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can create a chat room.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to create chat room
            chat_type: Type of chat room to create
            course: Course for course chat rooms
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can create chat room, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to create chat rooms"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        if chat_type == "course":
            if user.role != "teacher":
                error_msg = "Only teachers can create course chat rooms"
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                if permission_obj:
                    permission_obj.message = error_msg
                return False

            if course and course.teacher != user:
                error_msg = (
                    "You can only create chat rooms for courses you teach"
                )
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                if permission_obj:
                    permission_obj.message = error_msg
                return False

        return True

    @staticmethod
    def check_can_access_chat_room(
        user: User,
        chat_room: ChatRoom,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can access a chat room.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to access chat room
            chat_room: Chat room to access
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can access chat room, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to access chat rooms"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Public chats: accessible to everyone
        if chat_room.is_public:
            return True

        # Private chats: only accessible to participants
        if chat_room.participants.filter(user=user, is_active=True).exists():
            return True

        # Course chats: accessible to course teacher
        if chat_room.course and chat_room.course.teacher == user:
            return True

        error_msg = "You do not have access to this chat room"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        if permission_obj:
            permission_obj.message = error_msg
        return False

    @staticmethod
    def check_can_modify_chat_room(
        user: User,
        chat_room: ChatRoom,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can modify a chat room.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to modify chat room
            chat_room: Chat room to modify
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can modify chat room, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify chat rooms"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Only creator can modify
        if chat_room.created_by != user:
            error_msg = "Only the creator can modify this chat room"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True

    @staticmethod
    def check_can_manage_participants(
        user: User,
        chat_room: ChatRoom,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can manage participants in a chat room.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to manage participants
            chat_room: Chat room to manage participants in
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can manage participants, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to manage participants"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Only admins can manage participants
        try:
            participant = chat_room.participants.get(user=user)
            if participant.role != "admin":
                error_msg = "Only admins can manage participants"
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                if permission_obj:
                    permission_obj.message = error_msg
                return False
            return True
        except ChatParticipant.DoesNotExist:
            error_msg = "You must be a participant to manage this chat room"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False
