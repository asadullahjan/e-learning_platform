from rest_framework.permissions import BasePermission
from elearning.models import ChatParticipant
from elearning.exceptions import ServiceError
from .chat_room_permissions import ChatPolicy


class ChatMessagePermission(BasePermission):
    """DRF permission class for chat message operations"""

    def has_permission(self, request, view):
        # Must be authenticated for all except list
        if view.action == "list":
            return request.user.is_authenticated

        if view.action == "create":
            chat_room_pk = request.data.get("chat_room") or view.kwargs.get(
                "chat_room_pk"
            )
            return (
                request.user.is_authenticated
                and chat_room_pk
                and self._is_participant(request.user, chat_room_pk)
            )

        if view.action in ["partial_update", "destroy"]:
            return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ["partial_update", "destroy"]:
            # Sender can always edit/delete their own messages
            if obj.sender == request.user:
                return True
            # Otherwise must be admin in chat room
            return self._is_admin(request.user, obj.chat_room.id)
        return True

    def _is_participant(self, user, chat_room_pk):
        """Check if user is an active participant of the chat room"""
        try:
            ChatParticipant.objects.get(
                chat_room_id=chat_room_pk, user=user, is_active=True
            )
            return True
        except ChatParticipant.DoesNotExist:
            return False

    def _is_admin(self, user, chat_room_pk):
        """Check if user is an admin of the chat room"""
        try:
            ChatParticipant.objects.get(
                chat_room_id=chat_room_pk, user=user, role="admin"
            )
            return True
        except ChatParticipant.DoesNotExist:
            return False


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

    @staticmethod
    def check_can_view_message(user, message, raise_exception=False):
        """Check if user can view a message"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to view messages"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Check if user can access the chat room
        return ChatPolicy.check_can_access_chat_room(
            user, message.chat_room, raise_exception
        )
