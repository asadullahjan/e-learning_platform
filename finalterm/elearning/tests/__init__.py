# Import all tests for easy access
from .test_auth import AuthenticationTest
from .test_profile_views import UserProfileTest
from .test_models import UserModelTest
from .test_course_views import CourseViewsTest
from .test_enrollment_views import EnrollmentViewsTest

__all__ = [
    "AuthenticationTest",
    "UserProfileTest",
    "UserModelTest",
    "CourseViewsTest",
    "EnrollmentViewsTest",
]
