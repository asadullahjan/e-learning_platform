"""
User-related permissions for the eLearning platform.

This package contains permission classes that control access to user-related
functionality such as profile viewing, status updates, and user management.
"""

from .user_permissions import IsUserOwner
from .status_permissions import StatusPermission
from .notification_permissions import NotificationPermission

__all__ = [
    'IsUserOwner',
    'StatusPermission',
    'NotificationPermission',
]
