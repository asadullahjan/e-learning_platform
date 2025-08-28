"""
User notification permissions.

This module contains permission classes that control access to user
notifications such as viewing and marking notifications as read.
"""

from rest_framework.permissions import BasePermission
from elearning.models import Notification, User
from elearning.exceptions import ServiceError


class NotificationPermission(BasePermission):
    """
    Custom permission for notifications - users can only see their own.

    Simple permission check without complex DB queries.
    Object-level permission checking ensures users only access their own
    notifications.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access notifications"
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can access specific notification object"""
        # Users can only access their own notifications
        return obj.user == request.user


class NotificationPolicy:
    """
    Policy class for user notification operations.

    This class encapsulates all business rules for notification operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_view_notification(
        user: User,
        notification: Notification,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can view a notification.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to view notification
            notification: Notification object to view
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
    def check_can_mark_notification_read(
        user: User,
        notification: Notification,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can mark a notification as read.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to mark notification as read
            notification: Notification object to mark as read
            raise_exception: If True, raises ServiceError instead of
                returning False

        Returns:
            bool: True if user can mark notification as read, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to mark notifications as read"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Users can only mark their own notifications as read
        if notification.user != user:
            error_msg = "You can only mark your own notifications as read"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_delete_notification(
        user: User,
        notification: Notification,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can delete a notification.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to delete notification
            notification: Notification object to delete
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
