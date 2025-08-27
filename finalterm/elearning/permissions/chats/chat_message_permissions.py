from rest_framework.permissions import BasePermission
from elearning.models import ChatParticipant
from elearning.exceptions import ServiceError


class ChatMessagePermission(BasePermission):
    """DRF permission class for chat message operations - basic checks only"""

    def has_permission(self, request, view):
        """Basic permission checks without database queries"""

        # For list action, allow all users
        # (public chats can be viewed by anyone, private chats require auth)
        if view.action == "list":
            return True

        # For other actions, require authentication
        if view.action in ["create", "partial_update", "destroy"]:
            return request.user.is_authenticated

        return True

    def has_object_permission(self, request, view, obj):
        """Object-level permission checks"""
        if view.action in ["partial_update", "destroy"]:
            # Sender can always edit/delete their own messages
            if obj.sender == request.user:
                return True
            # For other users, detailed checks will be done in service layer
            return True
        return True


class ChatMessagePolicy:
    """Policy class for chat message operations"""

    @staticmethod
    def check_can_create_message(user, chat_room, raise_exception=False):
        """Check if user can create a message in the chat room"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to send messages"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Check if user is an active participant
        try:
            ChatParticipant.objects.get(
                chat_room=chat_room, user=user, is_active=True
            )
            return True
        except ChatParticipant.DoesNotExist:
            error_msg = (
                "You must be a participant to send messages in this chat"
            )
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

    @staticmethod
    def check_can_modify_message(user, message, raise_exception=False):
        """Check if user can modify (edit/delete) a message"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify messages"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Sender can always edit/delete their own messages
        if message.sender == user:
            return True

        # Check if user is admin in the chat room
        try:
            ChatParticipant.objects.get(
                chat_room=message.chat_room, user=user, role="admin"
            )
            return True
        except ChatParticipant.DoesNotExist:
            error_msg = "You can only edit your own messages"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False
