"""
User profile and management permissions.

This module contains permission classes that control access to user profiles
and user management operations.
"""

from rest_framework.permissions import BasePermission


class IsUserOwner(BasePermission):
    """
    Permission class for user profile operations.
    
    Users can only view and modify their own profiles.
    This ensures privacy and data security.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the owner of the profile"""
        return obj == request.user
