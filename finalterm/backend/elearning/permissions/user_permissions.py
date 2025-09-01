"""
User profile and management permissions.

This module contains permission classes that control access to user profiles
and user management operations.
"""

from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission
from elearning.models import User
from elearning.exceptions import ServiceError


class IsUserAuthenticatedAndOwner(BasePermission):
    """
    Permission class for user profile operations.

    Any authenticated user can view any profile.
    Users can only modify their own profiles.
    """

    def has_permission(self, request, view):
        """Check if user is authenticated"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access user profiles"
            raise NotAuthenticated(self.message)
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can access the profile object"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access user profiles"
            raise NotAuthenticated(self.message)

        # For read operations, any authenticated user can access
        if view.action in ["list", "retrieve"]:
            return True

        # For write operations, only the profile owner can access
        if view.action in ["update", "partial_update", "destroy"]:
            if obj != request.user:
                self.message = "You can only modify your own profile"
                return False

        return True


class UserPolicy:
    """
    Policy class for user operations.

    This class encapsulates all business rules for user operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_view_profile(
        user: User,
        target_user: User,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can view another user's profile.

        Any authenticated user can view any profile.

        Args:
            user: User attempting to view profile
            target_user: User whose profile is being viewed
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can view profile, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to view user profiles"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Any authenticated user can view any profile
        return True

    @staticmethod
    def check_can_modify_profile(
        user: User,
        target_user: User,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can modify another user's profile.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError instead of
        returning False

        Args:
            user: User attempting to modify profile
            target_user: User whose profile is being modified
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can modify profile, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify user profiles"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Users can only modify their own profile
        if user != target_user:
            error_msg = "You can only modify your own profile"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True

    @staticmethod
    def check_can_delete_user(
        user: User,
        target_user: User,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can delete another user.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError instead of
        returning False

        Args:
            user: User attempting to delete
            target_user: User to be deleted
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can delete, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to delete users"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Users cannot delete themselves
        if user == target_user:
            error_msg = "You cannot delete your own account"
            if raise_exception:
                raise ServiceError.bad_request(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Only superusers can delete users
        if not user.is_superuser:
            error_msg = "Only administrators can delete users"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True
