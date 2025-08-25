"""
Authentication and role-based permissions.

This module contains permission classes that control access based on user
roles such as teacher, student, and admin permissions.
"""

from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    """
    Permission class for teacher-only operations.
    
    Only users with teacher role can access these endpoints.
    This ensures teachers have appropriate access to course management.
    """
    
    def has_permission(self, request, view):
        """Check if user has teacher role"""
        return request.user.is_authenticated and request.user.role == "teacher"


class IsTeacherOrAdmin(BasePermission):
    """
    Permission class for teacher or admin operations.
    
    Allows both teachers and superusers to access these endpoints.
    This provides flexibility for administrative operations.
    """
    
    def has_permission(self, request, view):
        """Check if user has teacher role or is superuser"""
        return request.user.is_authenticated and (
            request.user.role == "teacher" or request.user.is_superuser
        )


class IsStudent(BasePermission):
    """
    Permission class for student-only operations.
    
    Only users with student role can access these endpoints.
    This ensures students have appropriate access to student features.
    """
    
    def has_permission(self, request, view):
        """Check if user has student role"""
        return request.user.is_authenticated and request.user.role == "student"
