# Import all tests for easy access
from .test_auth import AuthenticationTest
from .test_profile_views import UserProfileTest
from .test_models import UserModelTest
from .chats import (
    ChatRoomViewsTestCase,
    ChatMessageViewsTestCase,
    ChatParticipantViewsTestCase,
    WebSocketIntegrationTest,
)
from .test_notification_views import NotificationViewSetTest
from .courses import (
    CourseViewsTest,
    CourseLessonViewSetTestCase,
    CourseFeedbackViewsTestCase,
    StudentRestrictionViewsTestCase,
    EnrollmentViewsTest,
)

__all__ = [
    "AuthenticationTest",
    "UserProfileTest",
    "UserModelTest",
    "CourseViewsTest",
    "EnrollmentViewsTest",
    "NotificationViewSetTest",
    "CourseLessonViewSetTestCase",
    "CourseFeedbackViewsTestCase",
    "StudentRestrictionViewsTestCase",
    "ChatRoomViewsTestCase",
    "ChatMessageViewsTestCase",
    "ChatParticipantViewsTestCase",
    "WebSocketIntegrationTest",
]
