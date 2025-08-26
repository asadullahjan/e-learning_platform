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
from .courses.course_service import CourseService
from .courses.enrollment_service import EnrollmentService
from .courses.student_restriction_service import StudentRestrictionService
from .courses.course_lesson_service import CourseLessonService
from .courses.course_feedback_service import CourseFeedbackService
from .chats.chat_service import ChatService
from .chats.chat_messages_service import ChatMessagesService
from .chats.chat_participants_service import ChatParticipantsService
from .chats.chat_websocket_service import ChatWebSocketService
from .user_service import UserService
from .notification_service import NotificationService
from .status_service import StatusService

__all__ = [
    # Course services
    "CourseService",
    "EnrollmentService",
    "StudentRestrictionService",
    "CourseLessonService",
    "CourseFeedbackService",
    # Chat services
    "ChatService",
    "ChatMessagesService",
    "ChatParticipantsService",
    "ChatWebSocketService",
    # User services
    "UserService",
    # Other services
    "NotificationService",
    "StatusService",
]
