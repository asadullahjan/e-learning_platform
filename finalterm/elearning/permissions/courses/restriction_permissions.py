"""
Student restriction permissions.

This module contains permission classes that control access to student 
restriction operations such as creating, viewing, and deleting restrictions.
"""

from rest_framework.permissions import BasePermission


class StudentRestrictionPermission(BasePermission):
    """
    Permission class for student restrictions.
    
    Only teachers can create/delete restrictions.
    Teachers can only manage their own restrictions.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to manage restrictions"""
        # Must be authenticated and a teacher
        if not request.user.is_authenticated:
            return False
        
        if request.user.role != "teacher":
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage specific restriction object"""
        # Teachers can only manage their own restrictions
        return obj.teacher == request.user
