# Import all tests for easy access
from .test_auth import AuthenticationTest
from .test_profile_views import UserProfileTest
from .chats import (
    ChatRoomViewsTestCase,
    ChatMessageViewsTestCase,
    ChatParticipantViewsTestCase,
    ChatWebSocketTestCase,
)
from .test_notification_views import NotificationViewSetTest
from .courses import (
    CourseViewsTestCase,
    CourseLessonViewSetTestCase,
    CourseFeedbackViewsTestCase,
    CourseStudentRestrictionViewsTestCase,
    CourseEnrollmentViewsTest,
)

__all__ = [
    "AuthenticationTest",
    "UserProfileTest",
    "CourseViewsTestCase",
    "CourseEnrollmentViewsTest",
    "NotificationViewSetTest",
    "CourseLessonViewSetTestCase",
    "CourseFeedbackViewsTestCase",
    "CourseStudentRestrictionViewsTestCase",
    "ChatRoomViewsTestCase",
    "ChatMessageViewsTestCase",
    "ChatParticipantViewsTestCase",
    "ChatWebSocketTestCase",
]
