from rest_framework.permissions import BasePermission
from elearning.models import ChatRoom, ChatParticipant
from elearning.exceptions import ServiceError


class ChatParticipantPermission(BasePermission):
    """DRF permission class for chat participant operations"""

    def has_permission(self, request, view):
        chat_room_pk = view.kwargs.get("chat_room_pk")

        if not chat_room_pk:
            return False

        try:
            chat_room = ChatRoom.objects.get(id=chat_room_pk)
            request.chat_room = chat_room
        except ChatRoom.DoesNotExist:
            return False

        if view.action == "list":
            return True

        if not request.user.is_authenticated:
            return False

        if view.action == "create":
            # Check if user is adding someone else
            # (admin only) or joining themselves
            username = request.data.get("username")
            if username:
                # Adding another user - only admins or direct chat creators
                # can do this
                if (
                    chat_room.chat_type == "direct"
                    and chat_room.created_by == request.user
                ):
                    return True
                return ChatParticipant.objects.filter(
                    chat_room=chat_room, user=request.user, role="admin"
                ).exists()
            else:
                # Joining themselves - check if chat is public
                return chat_room.is_public

        if view.action == "update_role":
            # Only admins can update roles
            if (
                chat_room.chat_type == "direct"
                and chat_room.created_by == request.user
            ):
                return True
            return ChatParticipant.objects.filter(
                chat_room=chat_room, user=request.user, role="admin"
            ).exists()

        if view.action in ["deactivate", "reactivate"]:
            # Users can deactivate/reactivate themselves,
            # admins can do it for others
            return True

        if view.action == "destroy":
            # Only admins can remove participants
            if (
                chat_room.chat_type == "direct"
                and chat_room.created_by == request.user
            ):
                return True
            return ChatParticipant.objects.filter(
                chat_room=chat_room, user=request.user, role="admin"
            ).exists()

        # Default: only chat creator has access
        return request.user == chat_room.created_by


class ChatParticipantPolicy:
    """Policy class for chat participant operations"""

    @staticmethod
    def check_can_add_participant(user, chat_room, raise_exception=False):
        """Check if user can add participants to a chat room"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to add participants"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Direct chat creators can add participants
        if chat_room.chat_type == "direct" and chat_room.created_by == user:
            return True

        # Admins can add participants
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, role="admin"
        ).exists():
            return True

        error_msg = "Only admins can add participants to this chat"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_remove_participant(
        user, chat_room, target_user, raise_exception=False
    ):
        """Check if user can remove a participant from a chat room"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to remove participants"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users can remove themselves
        if user == target_user:
            return True

        # Direct chat creators can remove participants
        if chat_room.chat_type == "direct" and chat_room.created_by == user:
            return True

        # Admins can remove participants
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, role="admin"
        ).exists():
            return True

        error_msg = "Only admins can remove participants from this chat"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_update_participant_role(
        user, chat_room, raise_exception=False
    ):
        """Check if user can update participant roles"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to update participant roles"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Direct chat creators can update roles
        if chat_room.chat_type == "direct" and chat_room.created_by == user:
            return True

        # Admins can update roles
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, role="admin"
        ).exists():
            return True

        error_msg = "Only admins can update participant roles"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_join_chat(user, chat_room, raise_exception=False):
        """Check if user can join a chat room"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to join chats"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Public chats can be joined by anyone
        if chat_room.is_public:
            return True

        # Private chats require invitation
        error_msg = "This chat is private and requires an invitation"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False
