"""
Course permissions.

This module contains permission classes that control access to course
operations such as creating, viewing, editing, and deleting courses.
"""

from rest_framework import permissions
from elearning.models import Course, User
from elearning.exceptions import ServiceError


class CoursePermission(permissions.BasePermission):
    """DRF permission class for course operations - basic checks only"""

    def has_permission(self, request, view):
        """Basic permission checks without database queries"""
        if view.action in ["list", "retrieve"]:
            return True  # Anyone can view courses
        # For create, check if user is teacher
        if view.action == "create":
            return request.user.is_authenticated and request.user.role == "teacher"
        # For update/delete, require authentication (object check below)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions without database queries"""
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view (service handles published/unpublished)
        
        # Only course owners can modify/delete their courses
        return obj.teacher == request.user


class CourseAccessPermission(permissions.BasePermission):
    """DRF permission class for course access operations - basic checks only"""

    def has_permission(self, request, view):
        """Basic permission checks without database queries"""
        if view.action in ["list", "retrieve"]:
            return True  # Anyone can view courses
        return request.user.is_authenticated


class CoursePolicy:
    """
    Policy class for course operations.

    This class encapsulates all business rules for course operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_create_course(user: User, raise_exception=False) -> bool:
        """
        Check if a user can create a course.

        Args:
            user: User attempting to create a course
            raise_exception: If True, raises ServiceError instead of
                returning False

        Returns:
            bool: True if user can create course, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to create a course"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if user.role != "teacher":
            error_msg = "Only teachers can create courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_access_course(
        user: User, course: Course, raise_exception=False
    ) -> bool:
        """
        Check if user can access a specific course.

        Args:
            user: User attempting to access the course
            course: Course object to check access for
            raise_exception: If True, raises ServiceError instead of
                returning False

        Returns:
            bool: True if user can access, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            if not course.published_at:
                error_msg = "This course is not published"
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                return False
            return True

        if user.role == "teacher":
            if not course.published_at and course.teacher != user:
                error_msg = (
                    "This course is not published and you are not the teacher"
                )
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                return False
            return True

        # Students can only access published courses
        if not course.published_at:
            error_msg = "This course is not published"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_modify_course(
        user: User, course: Course, raise_exception=False
    ) -> bool:
        """
        Check if user can modify a course.

        Args:
            user: User attempting to modify the course
            course: Course object to modify
            raise_exception: If True, raises ServiceError instead of
                returning False

        Returns:
            bool: True if user can modify, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify a course"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if course.teacher != user:
            error_msg = "You can only edit or delete your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        return True

    @staticmethod
    def check_can_delete_course(
        user: User, course: Course, raise_exception=False
    ) -> bool:
        """
        Check if user can delete a course.

        Args:
            user: User attempting to delete the course
            course: Course object to delete
            raise_exception: If True, raises ServiceError instead of
                returning False

        Returns:
            bool: True if user can delete, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to delete a course"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        if course.teacher != user:
            error_msg = "You can only delete your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Check if course has enrollments
        if course.enrollments.exists():
            error_msg = "Cannot delete course with active enrollments"
            if raise_exception:
                raise ServiceError.conflict(error_msg)
            return False

        return True
