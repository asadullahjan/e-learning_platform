# Import all tests for easy access
from .test_auth import AuthenticationTest
from .users import UserProfileTest
from .test_models import UserModelTest
from .courses import CourseViewsTest

__all__ = [
    "AuthenticationTest",
    "UserProfileTest",
    "UserModelTest",
    "CourseViewsTest",
]
