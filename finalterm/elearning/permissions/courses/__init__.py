"""
Course-related permissions for the eLearning platform.

This package contains permission classes that control access to course-related
functionality such as course creation, enrollment, feedback, and restrictions.
"""

from .lesson_permissions import (
    LessonPermission,
    LessonPolicy,
)
from .feedback_permissions import (
    CourseFeedbackPermission,
    CourseFeedbackPolicy,
)
from .restriction_permissions import StudentRestrictionPermission
from .course_permissions import (
    CoursePermission,
    CourseAccessPermission,
    CoursePolicy,
)
from .enrollment_permissions import EnrollmentPermission, EnrollmentPolicy

__all__ = [
    "LessonPermission",
    "CourseFeedbackPermission",
    "StudentRestrictionPermission",
    "CourseFeedbackPolicy",
    "CoursePermission",
    "CourseAccessPermission",
    "CoursePolicy",
    "EnrollmentPermission",
    "EnrollmentPolicy",
    "LessonPolicy",
]
