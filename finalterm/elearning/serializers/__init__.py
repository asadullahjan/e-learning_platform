# Import all serializers for easy access
from .user_serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserDetailSerializer,
)
from .course_serializers import (
    CourseSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
)
from .enrollment_serializers import (
    EnrollmentSerializer,
    StudentEnrollmentSerializer,
    TeacherEnrollmentSerializer,
)

__all__ = [
    "UserRegistrationSerializer",
    "UserLoginSerializer",
    "UserSerializer",
    "UserDetailSerializer",
    "CourseSerializer",
    "CourseListSerializer",
    "CourseDetailSerializer",
    "EnrollmentSerializer",
    "StudentEnrollmentSerializer",
    "TeacherEnrollmentSerializer",
]
