from .test_course_views import CourseViewsTestCase
from .test_course_lesson_views import CourseLessonViewSetTestCase
from .test_course_feedback_views import CourseFeedbackViewsTestCase
from .test_course_student_restriction_views import (
    CourseStudentRestrictionViewsTestCase,
)
from .test_course_enrollment_views import CourseEnrollmentViewsTest

__all__ = [
    "CourseViewsTestCase",
    "CourseLessonViewSetTestCase",
    "CourseFeedbackViewsTestCase",
    "CourseStudentRestrictionViewsTestCase",
    "CourseEnrollmentViewsTest",
]
