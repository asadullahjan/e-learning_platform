"""
Centralized permissions package for the eLearning platform.

This package organizes all permission classes into logical categories:
- auth: Authentication and role-based permissions
- courses: Course-related permissions (ownership, enrollment, lessons, 
  feedback)
- users: User profile and status permissions
- chats: Chat room, message, and participant permissions

All permissions follow Django REST Framework best practices and provide
clear, documented access control for the platform.
"""

# Import all permission classes for easy access
from .auth import IsTeacher, IsTeacherOrAdmin, IsStudent
from .courses import (
    IsCourseOwner, 
    IsCourseOwnerOrEnrollmentOwner,
    LessonDownloadPermission,
    IsEnrolledInCourse,
    FeedbackPermission,
    StudentRestrictionPermission
)
from .users import IsUserOwner, StatusPermission, NotificationPermission
from .chats import (
    ChatRoomPermission,
    ChatMessagePermission,
    ChatParticipantPermission
)

__all__ = [
    # Auth permissions
    'IsTeacher',
    'IsTeacherOrAdmin',
    'IsStudent',
    
    # Course permissions
    'IsCourseOwner',
    'IsCourseOwnerOrEnrollmentOwner',
    'LessonDownloadPermission',
    'IsEnrolledInCourse',
    'FeedbackPermission',
    'StudentRestrictionPermission',
    
    # User permissions
    'IsUserOwner',
    'StatusPermission',
    'NotificationPermission',
    
    # Chat permissions
    'ChatRoomPermission',
    'ChatMessagePermission',
    'ChatParticipantPermission',
]
