"""
Course feedback permissions.

This module contains permission classes that control access to course feedback
operations such as creating, viewing, editing, and deleting feedback.
"""

from rest_framework import permissions


class FeedbackPermission(permissions.BasePermission):
    """
    Permission class for course feedback operations.
    
    Allows:
    - Anyone to view feedback (read-only)
    - Enrolled students to create/edit their own feedback
    - Only feedback owners can edit/delete their feedback
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access feedback"""
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view feedback
        
        # Must be logged in to create/edit
        if not request.user.is_authenticated:
            return False
        
        # For create/update/delete, check if user is enrolled
        course_id = view.kwargs.get("course_pk")
        if course_id:
            try:
                from elearning.models import Course
                course = Course.objects.get(pk=course_id)
                # Check if user is actively enrolled
                if not course.enrollments.filter(
                    user=request.user, is_active=True
                ).exists():
                    return False
            except Course.DoesNotExist:
                return False
        
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can modify specific feedback object"""
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view feedback
        return obj.user == request.user  # Only owner can edit/delete
