"""
User status and activity permissions.

This module contains permission classes that control access to user status
updates and activity tracking functionality.
"""

from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission
from elearning.models import User, Status
from elearning.exceptions import ServiceError


class StatusPermission(BasePermission):
    """
    Permission class for user status operations.

    Controls who can view and modify user status updates.
    """

    def has_permission(self, request, view):
        """Check if user has permission to perform status operations"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access status features"
            raise NotAuthenticated(self.message)
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can access specific status object"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access status features"
            raise NotAuthenticated(self.message)

        # Users can always view their own status
        if obj.user == request.user:
            return True

        # Users can view other users' status (for social features)
        if view.action in ["retrieve", "list"]:
            return True

        # Only status owner can modify their status
        if view.action in ["update", "partial_update", "destroy"]:
            if obj.user != request.user:
                self.message = "You can only modify your own status"
                return False

        return True


class StatusPolicy:
    """
    Policy class for status operations.

    This class encapsulates all business rules for status operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_create_status(
        user: User,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can create a status update.

        Args:
            user: User attempting to create status
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can create status, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to create status updates"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Check if user has any active restrictions
        if hasattr(user, "studentrestriction_set"):
            active_restrictions = user.studentrestriction_set.filter(
                is_active=True
            )
            if active_restrictions.exists():
                error_msg = (
                    "Your account has restrictions that prevent "
                    "status updates"
                )
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                if permission_obj:
                    permission_obj.message = error_msg
                return False

        return True

    @staticmethod
    def check_can_view_status(
        user: User,
        status: Status,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can view a specific status.

        Args:
            user: User attempting to view status
            status: Status object to be viewed
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can view status, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to view status updates"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Users can always view their own status
        if status.user == user:
            return True

        # Check if status user has privacy restrictions
        if hasattr(status.user, "studentrestriction_set"):
            active_restrictions = status.user.studentrestriction_set.filter(
                is_active=True
            )
            if active_restrictions.exists():
                error_msg = (
                    "This user's status is not available due to "
                    "restrictions"
                )
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                if permission_obj:
                    permission_obj.message = error_msg
                return False

        return True

    @staticmethod
    def check_can_modify_status(
        user: User,
        status: Status,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can modify a specific status.

        Args:
            user: User attempting to modify status
            status: Status object to be modified
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can modify status, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify status updates"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Users can only modify their own status
        if status.user != user:
            error_msg = "You can only modify your own status updates"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Check if user has any active restrictions
        if hasattr(user, "studentrestriction_set"):
            active_restrictions = user.studentrestriction_set.filter(
                is_active=True
            )
            if active_restrictions.exists():
                error_msg = (
                    "Your account has restrictions that prevent "
                    "status updates"
                )
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                if permission_obj:
                    permission_obj.message = error_msg
                return False

        return True

    @staticmethod
    def check_can_delete_status(
        user: User,
        status: Status,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can delete a specific status.

        Args:
            user: User attempting to delete status
            status: Status object to be deleted
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can delete status, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to delete status updates"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Users can only delete their own status
        if status.user != user:
            error_msg = "You can only delete your own status updates"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True
