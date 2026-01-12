"""
Chat participant permissions.

This module contains permission classes that control access to chat
participant operations including adding, removing, and role management.
"""

from rest_framework.permissions import BasePermission
from elearning.models import ChatParticipant
from elearning.exceptions import ServiceError


class ChatParticipantPermission(BasePermission):
    """
    DRF permission class for chat participant operations.

    Provides basic permission checks for chat participant operations.
    Detailed business logic is handled by the ChatParticipantPolicy class.
    """

    def has_permission(self, request, view):
        """Basic permission checks without database queries"""

        # Check if user is authenticated for actions that require it
        if view.action in [
            "create",
            "update_role",
            "deactivate",
            "reactivate",
            "destroy",
        ]:
            if not request.user.is_authenticated:
                return False

        # For list action, allow all users
        if view.action == "list":
            return True

        # For other actions, basic checks passed - detailed checks will be done
        # in policies
        return True


class ChatParticipantPolicy:
    """
    Policy class for chat participant operations.

    Note: This policy does NOT check student restrictions directly. For course
    chats, access is determined by enrollment status (enrollment.is_active),
    which is automatically managed by the restriction service.
    """

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
        user, chat_room, target_user, raise_exception=False
    ):
        """Check if user can update participant roles"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to update participant roles"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users cannot change their own role
        if user == target_user:
            raise ServiceError.permission_denied("Cannot change your own role")

        if (
            not chat_room.chat_type == "direct"
            and chat_room.created_by == user
        ):
            return True

        error_msg = "Only chat creator can update participant roles"
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

    @staticmethod
    def check_can_get_participants(user, chat_room, raise_exception=False):
        """Check if user can get participants of a chat room"""
        # For public chats, anyone can see participants
        if chat_room.is_public:
            return True

        # For private chats, only participants can see participants
        if user.is_authenticated:
            if ChatParticipant.objects.filter(
                chat_room=chat_room, user=user, is_active=True
            ).exists():
                return True

        # Unauthenticated users can't see private chat participants
        error_msg = (
            "You must be logged in to view participants of private chats"
        )
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_deactivate_participant(
        user, chat_room, target_user, raise_exception=False
    ):
        """Check if user can deactivate a participant"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to deactivate participants"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False


        # Admins can not be deactivated
        if user == target_user and ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, role="admin"
        ).exists():
            error_msg = "Admins cannot be deactivated"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users can deactivate themselves
        if user == target_user:
            return True

        # Direct chat creators can deactivate participants
        if chat_room.chat_type == "direct" and chat_room.created_by == user:
            return True

        # Admins can deactivate participants
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, role="admin"
        ).exists():
            return True

        error_msg = "Only admins can deactivate participants from this chat"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_reactivate_participant(
        user, chat_room, target_user, raise_exception=False
    ):
        """Check if user can reactivate a participant"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to reactivate participants"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users can reactivate themselves
        if user == target_user:
            return True

        # Direct chat creators can reactivate participants
        if chat_room.chat_type == "direct" and chat_room.created_by == user:
            return True

        # Admins can reactivate participants
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user, role="admin"
        ).exists():
            return True

        error_msg = "Only admins can reactivate participants in this chat"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False
