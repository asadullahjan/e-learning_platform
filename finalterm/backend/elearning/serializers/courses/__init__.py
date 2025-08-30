from .course_serializers import (
    CourseReadOnlySerializer,
    CourseWriteSerializer,
    CourseListReadOnlySerializer,
)

from .course_enrollment_serializers import (
    CourseEnrollmentReadOnlyForStudentSerializer,
    CourseEnrollmentReadOnlyForTeacherSerializer,
    CourseEnrollmentWriteSerializer,
)

from .course_student_restriction_serializer import (
    CourseStudentRestrictionReadOnlySerializer,
    CourseStudentRestrictionWriteSerializer,
)

from .course_lesson_serializers import (
    CourseLessonReadOnlySerializer,
    CourseLessonWriteSerializer,
    CourseLessonListReadOnlySerializer,
)

from .course_feedback_serializers import (
    CourseFeedbackReadOnlySerializer,
    CourseFeedbackReadOnlyForTeacherSerializer,
    CourseFeedbackReadOnlyForUserSerializer,
    CourseFeedbackWriteSerializer,
)

__all__ = [
    # Course
    "CourseReadOnlySerializer",
    "CourseWriteSerializer",
    "CourseListReadOnlySerializer",
    # CourseEnrollment
    "CourseEnrollmentReadOnlyForStudentSerializer",
    "CourseEnrollmentReadOnlyForTeacherSerializer",
    "CourseEnrollmentWriteSerializer",
    # CourseStudentRestriction
    "CourseStudentRestrictionReadOnlySerializer",
    "CourseStudentRestrictionWriteSerializer",
    # CourseLesson
    "CourseLessonReadOnlySerializer",
    "CourseLessonWriteSerializer",
    "CourseLessonListReadOnlySerializer",
    # CourseFeedback
    "CourseFeedbackReadOnlySerializer",
    "CourseFeedbackReadOnlyForTeacherSerializer",
    "CourseFeedbackReadOnlyForUserSerializer",
    "CourseFeedbackWriteSerializer",
]
