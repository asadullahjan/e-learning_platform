"""
Authentication and role-based permissions.

This module contains permission classes that control access based on user
roles such as teacher, student, and admin permissions.
"""

from rest_framework.permissions import BasePermission
from elearning.exceptions import ServiceError


class AuthPermission(BasePermission):
    """Permission class for authentication operations"""

    def has_permission(self, request, view):
        # Allow all authentication operations
        return True


class AuthPolicy:
    """Policy class for authentication operations"""

    @staticmethod
    def check_can_register(user=None, raise_exception=False):
        """Check if user can register (no user means new registration)"""
        # Anyone can register (no user means new registration)
        return True

    @staticmethod
    def check_can_login(user, raise_exception=False):
        """Check if user can login"""
        if not user.is_active:
            error_msg = "Account is deactivated"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_change_password(user, raise_exception=False):
        """Check if user can change their password"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to change your password"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_reset_password(user=None, raise_exception=False):
        """Check if user can reset password (no user means forgot password)"""
        # Anyone can request password reset
        return True


# Centralized role-based permissions - NO DATABASE QUERIES
class RolePermission(BasePermission):
    """Base class for role-based permissions"""

    def has_permission(self, request, view):
        """Base permission check - must be authenticated"""
        return request.user.is_authenticated


class IsTeacher(RolePermission):
    """
    Permission class for teacher-only operations.

    Only users with teacher role can access these endpoints.
    This ensures teachers have appropriate access to course management.
    """

    def has_permission(self, request, view):
        """Check if user has teacher role - NO DB QUERY"""
        if not super().has_permission(request, view):
            return False
        return request.user.role == "teacher"


class IsTeacherOrAdmin(RolePermission):
    """
    Permission class for teacher or admin operations.

    Allows both teachers and superusers to access these endpoints.
    This provides flexibility for administrative operations.
    """

    def has_permission(self, request, view):
        """Check if user has teacher role or is superuser - NO DB QUERY"""
        if not super().has_permission(request, view):
            return False
        return request.user.role == "teacher" or request.user.is_superuser


class IsStudent(RolePermission):
    """
    Permission class for student-only operations.

    Only users with student role can access these endpoints.
    This ensures students have appropriate access to student features.
    """

    def has_permission(self, request, view):
        """Check if user has student role - NO DB QUERY"""
        if not super().has_permission(request, view):
            return False
        return request.user.role == "student"
