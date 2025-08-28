"""
Course enrollment permissions.

This module contains permission classes that control access to course
enrollment operations such as creating, viewing, and managing enrollments.
"""

from rest_framework import permissions
from elearning.models import Course, User, Enrollment
from elearning.exceptions import ServiceError


class EnrollmentPermission(permissions.BasePermission):
    """
    Permission class for course enrollment operations.

    Allows:
    - Authenticated users to view their own enrollments
    - Teachers to view enrollments for their courses
    - Students to enroll in published courses
    - Course owners to manage enrollments
    """

    def has_permission(self, request, view):
        """Basic permission checks (no DB yet)"""
        if not request.user.is_authenticated:
            return False

        if view.action in ["list"]:
            # Only teachers can list enrollments
            return request.user.role == "teacher"

        if view.action in ["create"]:
            # Only students can enroll
            return request.user.role == "student"

        # retrieve, update, partial_update, destroy
        return True  # defer to object-level checks

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions without database queries"""
        if request.method in permissions.SAFE_METHODS:
            # Users can view their own enrollments
            if obj.user == request.user:
                return True
            # Teachers can view enrollments for their courses
            if (
                request.user.role == "teacher"
                and obj.course.teacher == request.user
            ):
                return True
            return False

        # For update (activate/deactivate), allow students to modify their own
        # enrollment
        if view.action in ["update", "partial_update"]:
            if obj.user == request.user:
                return True
            # Teachers can modify enrollments for their courses
            if (
                request.user.role == "teacher"
                and obj.course.teacher == request.user
            ):
                return True
            return False

        return False


class EnrollmentPolicy:
    """
    Policy class for course enrollment operations.

    This class encapsulates all business rules for enrollment operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_enroll(
        user: User, course: Course, raise_exception=False
    ) -> bool:
        """
        Check if a user can enroll in a course.

        This method can be used by both permissions and services:
        - For permissions: returns boolean
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to enroll
            course: Course to enroll in

            raise_exception: If True, raises ServiceError instead of returning
            False

        Returns:
            bool: True if user can enroll, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to enroll in a course"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if user.role != "student":
            error_msg = "Only students can enroll in courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if not course.published_at:
            error_msg = "Cannot enroll in unpublished course"
            if raise_exception:
                raise ServiceError.bad_request(error_msg)

            return False

        # Check if already enrolled
        if Enrollment.objects.filter(
            user=user, course=course, is_active=True
        ).exists():
            error_msg = "You are already enrolled in this course"
            if raise_exception:
                raise ServiceError.conflict(error_msg)

            return False

        return True

    @staticmethod
    def check_can_view_enrollment(
        user: User,
        enrollment: Enrollment,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can view an enrollment.

        This method can be used by both permissions and services:
        - For permissions: returns boolean
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to view enrollment
            enrollment: Enrollment object to view

            raise_exception: If True, raises ServiceError instead of returning
            False

        Returns:
            bool: True if user can view, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to view enrollments"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        # Users can view their own enrollments
        if enrollment.user == user:
            return True

        # Teachers can view enrollments for their courses
        if user.role == "teacher" and enrollment.course.teacher == user:
            return True

        error_msg = "You can only view your own enrollments"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_modify_enrollment(
        user: User,
        enrollment: Enrollment,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can modify an enrollment.

        This method can be used by both permissions and services:
        - For permissions: returns boolean
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to modify enrollment
            enrollment: Enrollment object to modify

            raise_exception: If True, raises ServiceError instead of returning
            False

        Returns:
            bool: True if user can modify, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify enrollments"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        # Course owners can manage enrollments
        if user.role == "teacher" and enrollment.course.teacher == user:
            return True

        # Students can only modify their own enrollments
        if enrollment.user != user:
            error_msg = "You can only modify your own enrollments"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        return True

    @staticmethod
    def check_can_unenroll(
        user: User,
        enrollment: Enrollment,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can unenroll from a course.

        This method can be used by both permissions and services:
        - For permissions: returns boolean
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to unenroll
            enrollment: Enrollment object to unenroll from

            raise_exception: If True, raises ServiceError instead of returning
            False

        Returns:
            bool: True if user can unenroll, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to unenroll from a course"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        # Course owners can remove students
        if user.role == "teacher" and enrollment.course.teacher == user:
            return True

        # Students can only unenroll themselves
        if enrollment.user != user:
            error_msg = "You can only unenroll yourself from a course"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if not enrollment.is_active:
            error_msg = "You are not currently enrolled in this course"
            if raise_exception:
                raise ServiceError.bad_request(error_msg)

            return False

        return True
