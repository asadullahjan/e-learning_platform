"""
User status update permissions.

This module contains permission classes that control access to user status
operations such as creating, viewing, editing, and deleting status updates.
"""

from rest_framework.permissions import BasePermission
from elearning.models import Status, User
from elearning.exceptions import ServiceError


class StatusPermission(BasePermission):
    """
    Object-level permission class for status operations.
    
    IsAuthenticated handles authentication, this handles object permissions.
    Users can view all statuses but only edit/delete their own.
    """
    
    def has_permission(self, request, view):
        """Check if user can access the view"""
        # All actions require authentication
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access status updates"
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can modify specific status object"""
        # Only status owner can edit/delete their own status
        if view.action in ["update", "partial_update", "destroy"]:
            if obj.user != request.user:
                self.message = "You can only edit or delete your own status updates"
                return False
        return True


class StatusPolicy:
    """
    Policy class for user status operations.

    This class encapsulates all business rules for status operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_create_status(
        user: User, raise_exception=False
    ) -> bool:
        """
        Check if a user can create a status.
        
        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to create status
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
            return False

        return True

    @staticmethod
    def check_can_view_status(
        user: User, status: Status, permission_obj=None, raise_exception=False
    ) -> bool:
        """
        Check if a user can view a status.
        
        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to view status
            status: Status object to view
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of returning False

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

        # Anyone can view statuses
        return True

    @staticmethod
    def check_can_modify_status(
        user: User, status: Status, permission_obj=None, raise_exception=False
    ) -> bool:
        """
        Check if a user can modify a status.
        
        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to modify status
            status: Status object to modify
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of returning False

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

        # Only status owner can modify their own status
        if status.user != user:
            error_msg = "You can only edit or delete your own status updates"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True

    @staticmethod
    def check_can_delete_status(
        user: User, status: Status, permission_obj=None, raise_exception=False
    ) -> bool:
        """
        Check if a user can delete a status.
        
        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to delete status
            status: Status object to delete
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of returning False

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

        # Only status owner can delete their own status
        if status.user != user:
            error_msg = "You can only delete your own status updates"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True
