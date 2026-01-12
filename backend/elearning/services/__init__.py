"""
Services package for the eLearning platform.

This package contains all business logic services organized by domain:
- courses: Course, enrollment, lesson, and restriction services
- chats: Chat room, message, and participant services
- users: User management and profile services
- notifications: Notification and messaging services
- status: User status update services
"""

# Import all service classes for easy access
from .user_service import UserService
from .notification_service import NotificationService
from .status_service import StatusService

__all__ = [
    # User services
    "UserService",
    # Other services
    "NotificationService",
    "StatusService",
]
