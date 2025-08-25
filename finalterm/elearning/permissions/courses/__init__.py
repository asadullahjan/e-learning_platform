"""
Course-related permissions for the eLearning platform.

This package contains permission classes that control access to course-related
functionality such as course creation, enrollment, feedback, and restrictions.
"""

from .course_permissions import IsCourseOwner, IsCourseOwnerOrEnrollmentOwner
from .lesson_permissions import LessonDownloadPermission, IsEnrolledInCourse
from .feedback_permissions import FeedbackPermission
from .restriction_permissions import StudentRestrictionPermission

__all__ = [
    'IsCourseOwner',
    'IsCourseOwnerOrEnrollmentOwner', 
    'LessonDownloadPermission',
    'IsEnrolledInCourse',
    'FeedbackPermission',
    'StudentRestrictionPermission',
]
