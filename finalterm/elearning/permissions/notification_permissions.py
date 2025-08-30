"""
User notification permissions.

This module contains permission classes that control access to user
notifications and notification management functionality.
"""

from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission
from elearning.models import User, Notification
from elearning.exceptions import ServiceError


class NotificationPermission(BasePermission):
    """
    Permission class for user notification operations.

    Controls who can view and manage user notifications.
    """

    def has_permission(self, request, view):
        """Check if user has permission to perform notification operations"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access notifications"
            raise NotAuthenticated(self.message)
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can access specific notification object"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access notifications"
            raise NotAuthenticated(self.message)

        # Users can only access their own notifications
        if obj.user != request.user:
            self.message = "You can only access your own notifications"
            return False

        return True


class NotificationPolicy:
    """
    Policy class for notification operations.

    This class encapsulates all business rules for notification operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_view_notification(
        user: User,
        notification: Notification,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can view a specific notification.

        Args:
            user: User attempting to view notification
            notification: Notification object to be viewed
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can view notification, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to view notifications"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users can only view their own notifications
        if notification.user != user:
            error_msg = "You can only view your own notifications"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_mark_as_read(
        user: User,
        notification: Notification,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can mark a notification as read.

        Args:
            user: User attempting to mark notification as read
            notification: Notification object to be marked as read
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can mark notification as read, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify notifications"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users can only modify their own notifications
        if notification.user != user:
            error_msg = "You can only modify your own notifications"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_delete_notification(
        user: User,
        notification: Notification,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can delete a specific notification.

        Args:
            user: User attempting to delete notification
            notification: Notification object to be deleted
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can delete notification, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to delete notifications"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users can only delete their own notifications
        if notification.user != user:
            error_msg = "You can only delete your own notifications"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_create_notification(
        user: User,
        target_user: User,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can create a notification for another user.

        Args:
            user: User attempting to create notification
            target_user: User who will receive the notification
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can create notification, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to create notifications"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users cannot create notifications for themselves
        if user == target_user:
            error_msg = "You cannot create notifications for yourself"
            if raise_exception:
                raise ServiceError.bad_request(error_msg)
            return False

        # Only teachers and admins can create notifications for students
        if user.role not in ["teacher", "admin"]:
            error_msg = (
                "Only teachers and administrators can create " "notifications"
            )
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True
