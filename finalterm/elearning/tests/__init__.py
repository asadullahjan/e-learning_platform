# Import all tests for easy access
from .test_auth import AuthenticationTest
from .test_profile_views import UserProfileTest
from .test_models import UserModelTest
from .test_course_views import CourseViewsTest
from .test_enrollment_views import EnrollmentViewsTest
from .chats import ChatRoomViewsTestCase
from .test_notification_views import NotificationViewSetTest

__all__ = [
    "AuthenticationTest",
    "UserProfileTest",
    "UserModelTest",
    "CourseViewsTest",
    "EnrollmentViewsTest",
    "ChatRoomViewsTestCase",
    "NotificationViewSetTest",
]
