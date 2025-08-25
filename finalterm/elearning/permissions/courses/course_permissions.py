"""
Course ownership and enrollment permissions.

This module contains permission classes that control access to course 
operations such as creating, editing, deleting, and viewing course 
enrollments.
"""

from rest_framework.permissions import BasePermission


class IsCourseOwner(BasePermission):
    """
    Permission class for course ownership.
    
    Only the course creator (teacher) can edit/delete their own courses.
    This ensures teachers can only modify courses they have created.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the owner of the course"""
        return obj.teacher == request.user


class IsCourseOwnerOrEnrollmentOwner(BasePermission):
    """
    Permission class for course enrollment operations.
    
    Allows:
    - Course owners to view all enrollments for their courses
    - Users to view their own enrollment records
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is course owner or enrollment owner"""
        # Course owner can view enrollments for their course
        if obj.course.teacher == request.user:
            return True
        # User can view their own enrollment
        if obj.user == request.user:
            return True
        return False
