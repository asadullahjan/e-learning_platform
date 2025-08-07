# Import all tests for easy access
from .test_auth import AuthenticationTest
from .users import UserProfileTest
from .test_models import UserModelTest

__all__ = [
    "AuthenticationTest",
    "UserProfileTest",
    "UserModelTest",
]
