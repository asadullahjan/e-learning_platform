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
from .courses.course_lesson_serializers import (
    CourseLessonListSerializer,
    CourseLessonDetailSerializer,
    CourseLessonCreateSerializer,
    CourseLessonUpdateSerializer,
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
    "CourseLessonListSerializer",
    "CourseLessonDetailSerializer",
    "CourseLessonCreateSerializer",
    "CourseLessonUpdateSerializer",
]
