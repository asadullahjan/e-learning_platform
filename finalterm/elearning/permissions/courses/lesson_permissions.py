"""
Lesson access and download permissions.

This module contains permission classes that control access to course lessons
and lesson file downloads based on user enrollment and course ownership.
"""

from rest_framework.permissions import BasePermission
from elearning.exceptions import ServiceError


class LessonDownloadPermission(BasePermission):
    """
    Permission class for lesson file downloads.

    Allows:
    - Teachers to download files from their own courses
    - Students to download files from published lessons in courses
      they're enrolled in
    """

    def has_object_permission(self, request, view, obj):
        """Check if user can download lesson files - NO DB QUERY"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to download lesson files"
            return False

        # Teachers can download files from their own courses
        if obj.course.teacher == request.user:
            return True

        # Students can download files from published lessons in courses
        # they're enrolled in - enrollment check handled in service
        if obj.published_at:
            return True

        self.message = (
            "You do not have permission to download this lesson file"
        )
        return False


class IsEnrolledInCourse(BasePermission):
    """
    Permission class for viewing lessons.

    Allows:
    - Course owners (teachers) to view all lessons
    - Enrolled students to view published lessons
    """

    def has_permission(self, request, view):
        """Check if user has permission to view lessons - NO DB QUERY"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to view lessons"
            return False

        course_id = view.kwargs.get("course_pk")
        if not course_id:
            self.message = "Course ID is required"
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can view specific lesson object - NO DB QUERY"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to view lessons"
            return False

        # Course owners can view all lessons
        if obj.course.teacher == request.user:
            return True

        # Enrolled students can view published lessons
        # Enrollment check handled in service
        if obj.published_at:
            return True

        self.message = "You do not have permission to view this lesson"
        return False


class LessonPolicy:
    """
    Policy class for course lesson operations.

    This class encapsulates all business rules for lesson operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_view_lesson(user, lesson, raise_exception=False):
        """
        Check if a user can view a lesson.

        Args:
            user: User attempting to view lesson
            lesson: Lesson object to view
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can view, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to view lessons"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Course owners can view all lessons
        if lesson.course.teacher == user:
            return True

        # Enrolled students can view published lessons
        if (
            lesson.published_at
            and user.enrollments.filter(
                course=lesson.course, is_active=True
            ).exists()
        ):
            return True

        error_msg = "You do not have permission to view this lesson"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_create_lesson(user, course, raise_exception=False):
        """
        Check if a user can create a lesson.

        Args:
            user: User attempting to create lesson
            course: Course to create lesson in
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can create, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to create lessons"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if user.role != "teacher":
            error_msg = "Only teachers can create lessons"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if course.teacher != user:
            error_msg = "You can only create lessons in your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_modify_lesson(user, lesson, raise_exception=False):
        """
        Check if a user can modify a lesson.

        Args:
            user: User attempting to modify lesson
            lesson: Lesson object to modify
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can modify, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify lessons"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if user.role != "teacher":
            error_msg = "Only teachers can modify lessons"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if lesson.course.teacher != user:
            error_msg = "You can only modify lessons in your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_delete_lesson(user, lesson, raise_exception=False):
        """
        Check if a user can delete a lesson.

        Args:
            user: User attempting to delete lesson
            lesson: Lesson object to delete
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can delete, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to delete lessons"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if user.role != "teacher":
            error_msg = "Only teachers can delete lessons"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if lesson.course.teacher != user:
            error_msg = "You can only modify lessons in your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True
