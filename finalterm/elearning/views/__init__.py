# Import all views for easy access
from .auth_views import AuthViewSet
from .courses import (
    CourseViewSet,
    CourseLessonViewSet,
    EnrollmentViewSet,
    CourseEnrollmentViewSet,
)
from .courses.restrictions_views import StudentRestrictionViewSet
from .chats.chat_room_views import ChatRoomViewSet
from .chats.chat_participant_views import ChatParticipantViewSet
from .chats.chat_message_views import ChatMessageViewSet
from .status_views import StatusViewSet
from .user_views import UserViewSet
from .courses.feedback_views import FeedbackViewSet
from .notification_views import NotificationViewSet

__all__ = [
    "AuthViewSet",
    "CourseViewSet",
    "CourseLessonViewSet",
    "EnrollmentViewSet",
    "CourseEnrollmentViewSet",
    "StudentRestrictionViewSet",
    "ChatRoomViewSet",
    "ChatParticipantViewSet",
    "ChatMessageViewSet",
    "StatusViewSet",
    "UserViewSet",
    "FeedbackViewSet",
    "NotificationViewSet",
]
