# Import all serializers for easy access
from .users import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
)
from .courses import CourseSerializer, CourseDetailSerializer

__all__ = [
    "UserRegistrationSerializer",
    "UserLoginSerializer",
    "UserSerializer",
    "CourseSerializer",
    "CourseDetailSerializer",
]
