"""
Course permissions.

This module contains permission classes that control access to course
operations such as creating, viewing, editing, and deleting courses.
"""

from rest_framework import permissions
from elearning.models import Course, User
from elearning.exceptions import ServiceError


class CoursePermission(permissions.BasePermission):
    """
    Permission class for course operations.

    Allows:
    - Anyone to view published courses
    - Teachers to create courses
    - Course owners to edit/delete their courses
    """

    def has_permission(self, request, view):
        """Check if user has permission to access courses"""
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view courses

        # For create action, check if user is authenticated teacher
        if view.action == "create":
            if not request.user.is_authenticated:
                self.message = "You must be logged in to create a course"
                return False
            if request.user.role != "teacher":
                self.message = "Only teachers can create courses"
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can modify specific course object"""
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view published courses

        # Only course owners can modify courses
        if obj.teacher != request.user:
            self.message = "You can only edit or delete your own courses"
            return False

        return True


class CourseAccessPermission(permissions.BasePermission):
    """
    Permission class for course access operations.

    This is used for operations that require course access but not
    necessarily ownership (e.g., viewing course details, lessons).
    """

    def has_permission(self, request, view):
        """Check if user has permission to access course-related operations"""
        return True  # Will be checked at object level

    def has_object_permission(self, request, view, obj):
        """Check if user can access specific course object"""
        # For course-related objects, check course access
        if hasattr(obj, "course"):
            course = obj.course
        # For course objects directly
        elif hasattr(obj, "teacher"):
            course = obj
        else:
            return True

        # Basic access check - let service handle detailed validation
        if not course.published_at and not request.user.is_authenticated:
            self.message = "This course is not published"
            return False

        return True


class CoursePolicy:
    """
    Policy class for course operations.

    This class encapsulates all business rules for course operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_create_course(
        user: User, permission_obj=None, raise_exception=False
    ) -> bool:
        """
        Check if a user can create a course.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to create a course
            permission_obj: Permission object to set custom messages (optional)
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
            if permission_obj:
                permission_obj.message = error_msg
            return False

        if user.role != "teacher":
            error_msg = "Only teachers can create courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True

    @staticmethod
    def check_can_access_course(
        user: User, course: Course, permission_obj=None, raise_exception=False
    ) -> bool:
        """
        Check if user can access a specific course.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to access the course
            course: Course object to check access for
            permission_obj: Permission object to set custom messages (optional)
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
                if permission_obj:
                    permission_obj.message = error_msg
                return False
            return True

        if user.role == "teacher":
            if not course.published_at and course.teacher != user:
                error_msg = (
                    "This course is not published and you are not the teacher"
                )
                if raise_exception:
                    raise ServiceError.permission_denied(error_msg)
                if permission_obj:
                    permission_obj.message = error_msg
                return False
            return True

        # Students can only access published courses
        if not course.published_at:
            error_msg = "This course is not published"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True

    @staticmethod
    def check_can_modify_course(
        user: User, course: Course, permission_obj=None, raise_exception=False
    ) -> bool:
        """
        Check if user can modify a course.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to modify the course
            course: Course object to modify
            permission_obj: Permission object to set custom messages (optional)
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
            if permission_obj:
                permission_obj.message = error_msg
            return False

        if course.teacher != user:
            error_msg = "You can only edit or delete your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True

    @staticmethod
    def check_can_delete_course(
        user: User, course: Course, permission_obj=None, raise_exception=False
    ) -> bool:
        """
        Check if user can delete a course.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to delete the course
            course: Course object to delete
            permission_obj: Permission object to set custom messages (optional)
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
            if permission_obj:
                permission_obj.message = error_msg
            return False

        if course.teacher != user:
            error_msg = "You can only delete your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Check if course has enrollments
        if course.enrollments.exists():
            error_msg = "Cannot delete course with active enrollments"
            if raise_exception:
                raise ServiceError.conflict(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True
