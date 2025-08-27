"""
Lesson access and download permissions.

This module contains permission classes that control access to course lessons
and lesson file downloads based on user enrollment and course ownership.
"""

from rest_framework.permissions import BasePermission
from elearning.exceptions import ServiceError


class LessonPermission(BasePermission):
    """
    Single permission class for all lesson operations.

    Handles:
    - List/retrieve: Basic authentication and course access
    - Create/update/delete: Teacher role and course ownership
    - Download: File access permissions
    """

    def has_permission(self, request, view):
        """Basic permission checks without database queries"""
        if view.action in ["list", "retrieve"]:
            # Anyone can attempt to view lessons (service handles enrollment)
            if not request.user.is_authenticated:
                self.message = "You must be logged in to view lessons"
                return False

            course_id = view.kwargs.get("course_pk")
            if not course_id:
                self.message = "Course ID is required"
                return False

            return True

        elif view.action == "download":
            # Anyone authenticated can attempt download (object check below)
            return request.user.is_authenticated

        elif view.action in ["create", "update", "partial_update", "destroy"]:
            # Only teachers can modify lessons
            if not request.user.is_authenticated:
                self.message = "You must be logged in to modify lessons"
                return False

            if request.user.role != "teacher":
                self.message = "Only teachers can modify lessons"
                return False

            return True

        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions without database queries"""
        if not request.user.is_authenticated:
            return False

        if view.action in ["list", "retrieve"]:
            # Course owners can view all lessons
            if obj.course.teacher == request.user:
                return True

            # Students can view published lessons
            # (enrollment checked in service)
            if obj.published_at:
                return True

            self.message = "You do not have permission to view this lesson"
            return False

        elif view.action == "download":
            # Teachers can download files from their own courses
            if obj.course.teacher == request.user:
                return True

            # Students can download files from published lessons
            # (enrollment check handled in service)
            if obj.published_at:
                return True

            self.message = (
                "You do not have permission to download this lesson file"
            )
            return False

        elif view.action in ["update", "partial_update", "destroy"]:
            # Only course owners can modify their lessons
            if obj.course.teacher == request.user:
                return True

            self.message = "You can only modify lessons in your own courses"
            return False

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

        # Enrolled students can view published lessons in published courses
        if (
            lesson.published_at
            and lesson.course.published_at
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
            error_msg = "You can only delete lessons in your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True
