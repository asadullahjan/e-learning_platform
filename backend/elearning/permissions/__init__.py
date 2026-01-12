"""
Centralized permissions package for the eLearning platform.

This package organizes all permission classes and policy classes into
logical categories:
- auth: Authentication and role-based permissions
- courses: Course-related permissions (ownership, enrollment,
lessons, feedback)
- users: User profile and status permissions
- chats: Chat room, message, and participant permissions

All permissions follow Django REST Framework best practices and provide
clear, documented access control for the platform.
"""

from .user_permissions import UserPolicy, IsUserAuthenticatedAndOwner
from .status_permissions import StatusPermission, StatusPolicy
from .notification_permissions import (
    NotificationPermission,
    NotificationPolicy,
)

# Sub folders are exported from their respective __init__.py files
__all__ = [
    # Users
    "UserPolicy",
    "IsUserAuthenticatedAndOwner",
    "StatusPermission",
    "StatusPolicy",
    "NotificationPermission",
    "NotificationPolicy",
]
