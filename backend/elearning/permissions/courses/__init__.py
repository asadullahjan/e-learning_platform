"""
Course-related permissions for the eLearning platform.

This package contains permission classes that control access to course-related
functionality such as course creation, enrollment, feedback, and restrictions.
"""

# Permissions
from .course_lesson_permissions import CourseLessonPermission
from .course_feedback_permissions import CourseFeedbackPermission
from .course_restriction_permissions import CourseStudentRestrictionPermission
from .course_permissions import CoursePermission
from .course_enrollment_permissions import CourseEnrollmentPermission

# Policies
from .course_lesson_permissions import CourseLessonPolicy
from .course_feedback_permissions import CourseFeedbackPolicy
from .course_permissions import CoursePolicy
from .course_enrollment_permissions import CourseEnrollmentPolicy
from .course_file_permissions import CourseFilePolicy
from .course_restriction_permissions import CourseStudentRestrictionPolicy

__all__ = [
    # Permissions
    "CourseLessonPermission",
    "CourseFeedbackPermission",
    "CourseStudentRestrictionPermission",
    "CoursePermission",
    "CourseEnrollmentPermission",
    # Policies
    "CourseFeedbackPolicy",
    "CoursePolicy",
    "CourseEnrollmentPolicy",
    "CourseLessonPolicy",
    "CourseFilePolicy",
    "CourseStudentRestrictionPolicy",
]
