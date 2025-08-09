# Import all tests for easy access
from .test_auth import AuthenticationTest
from .users import UserProfileTest
from .test_models import UserModelTest
from .courses import CourseViewsTest
from .enrollments import EnrollmentViewsTest

__all__ = [
    "AuthenticationTest",
    "UserProfileTest",
    "UserModelTest",
    "CourseViewsTest",
    "EnrollmentViewsTest",
]
