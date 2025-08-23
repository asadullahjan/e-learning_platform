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
from .courses.course_feedback_serializer import (
    CourseFeedbackCreateUpdateSerializer,
    CourseFeedbackListSerializerForCourse,
    CourseFeedbackListSerializerForUser,
)
from .courses.student_restriction_serializer import (
    StudentRestrictionCreateUpdateSerializer,
    StudentRestrictionListSerializer,
)
from .notification_serializers import (
    NotificationSerializer,
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
    "CourseFeedbackCreateUpdateSerializer",
    "CourseFeedbackListSerializerForCourse",
    "CourseFeedbackListSerializerForUser",
    "StudentRestrictionCreateUpdateSerializer",
    "StudentRestrictionListSerializer",
    "NotificationSerializer",
]
