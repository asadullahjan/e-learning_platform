# Import all serializers for easy access
from .users import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserDetailSerializer,
)
from .courses import CourseSerializer, CourseDetailSerializer
from .enrollments import (
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
    "CourseDetailSerializer",
    "EnrollmentSerializer",
    "StudentEnrollmentSerializer",
    "TeacherEnrollmentSerializer",
]
