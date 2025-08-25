"""
User status update permissions.

This module contains permission classes that control access to user status
operations such as creating, viewing, editing, and deleting status updates.
"""

from rest_framework.permissions import BasePermission


class StatusPermission(BasePermission):
    """
    Object-level permission class for status operations.
    
    IsAuthenticated handles authentication, this handles object permissions.
    Users can view all statuses but only edit/delete their own.
    """
    
    def has_permission(self, request, view):
        """Check if user can access the view"""
        # All actions require authentication
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if user can modify specific status object"""
        # Only status owner can edit/delete their own status
        if view.action in ["update", "partial_update", "destroy"]:
            return obj.user == request.user
        return request.user.is_authenticated
