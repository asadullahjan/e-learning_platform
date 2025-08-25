"""
User notification permissions.

This module contains permission classes that control access to user 
notifications such as viewing and marking notifications as read.
"""

from rest_framework.permissions import IsAuthenticated


class NotificationPermission(IsAuthenticated):
    """
    Custom permission for notifications - users can only see their own.
    
    Extends IsAuthenticated to ensure users are logged in, then adds
    object-level permission checking to ensure users only access their
    own notifications.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can access specific notification object"""
        # Users can only access their own notifications
        return obj.user == request.user
