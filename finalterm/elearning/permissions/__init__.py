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

# Import all permission classes and policy classes for easy access
from .auth_permissions import (
    IsTeacher,
    IsTeacherOrAdmin,
    IsStudent,
    AuthPermission,
    AuthPolicy,
)
from .users.user_permissions import UserPolicy
from .users.status_permissions import StatusPermission, StatusPolicy
from .users.notification_permissions import (
    NotificationPermission,
    NotificationPolicy,
)

# Course-related permissions
from .courses.course_permissions import (
    CoursePermission, 
    CourseAccessPermission
)
from .courses.enrollment_permissions import EnrollmentPermission
from .courses.lesson_permissions import LessonPermission
from .courses.feedback_permissions import (
    CourseFeedbackPermission,
    CourseFeedbackPolicy,
)
from .courses.restriction_permissions import (
    StudentRestrictionPermission,
    StudentRestrictionPolicy,
)
from .courses.file_permissions import FilePolicy

# Chat-related permissions
from .chats.chat_room_permissions import ChatRoomPermission, ChatPolicy
from .chats.chat_participant_permissions import (
    ChatParticipantPermission,
    ChatParticipantPolicy,
)
from .chats.chat_message_permissions import (
    ChatMessagePermission,
    ChatMessagePolicy,
)

# Default permission classes for different resource types
__all__ = [
    # Auth
    "IsTeacher",
    "IsTeacherOrAdmin",
    "IsStudent",
    "AuthPermission",
    "AuthPolicy",
    # Users
    "UserPolicy",
    "StatusPermission",
    "StatusPolicy",
    "NotificationPermission",
    "NotificationPolicy",
    # Courses
    "CoursePermission",
    "CourseAccessPermission",
    "EnrollmentPermission",
    "LessonPermission",
    "CourseFeedbackPermission",
    "CourseFeedbackPolicy",
    "StudentRestrictionPermission",
    "StudentRestrictionPolicy",
    "FilePolicy",
    # Course Policies
    "CoursePolicy",
    "LessonPolicy",
    "EnrollmentPolicy",
    # Chats
    "ChatRoomPermission",
    "ChatPolicy",
    "ChatParticipantPermission",
    "ChatParticipantPolicy",
    "ChatMessagePermission",
    "ChatMessagePolicy",
]
