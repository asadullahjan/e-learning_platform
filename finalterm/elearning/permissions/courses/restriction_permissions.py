"""
Student restriction permissions.

This module contains permission classes that control access to student
restriction operations such as creating, viewing, and deleting restrictions.
"""

from rest_framework import permissions
from elearning.models import StudentRestriction, User, Course
from elearning.exceptions import ServiceError


class StudentRestrictionPermission(permissions.BasePermission):
    """
    Permission class for student restriction operations.

    Allows:
    - Teachers to create restrictions for students
    - Teachers to view and manage their own restrictions
    - Students to view restrictions applied to them
    """

    def has_permission(self, request, view):
        """Check if user has permission to access restrictions"""
        if not request.user.is_authenticated:
            self.message = "You must be logged in to access restrictions"
            return False

        # For list action, only teachers can access
        if view.action == "list":
            if request.user.role != "teacher":
                self.message = "Only teachers can view restrictions"
                return False

        # For create action, check if user is authenticated teacher
        if view.action == "create":
            if request.user.role != "teacher":
                self.message = "Only teachers can create restrictions"
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can modify specific restriction object"""
        if request.method in permissions.SAFE_METHODS:
            # Teachers can view their own restrictions
            if obj.teacher == request.user:
                return True
            # Students can view restrictions applied to them
            if obj.student == request.user:
                return True
            self.message = (
                "You can only view restrictions you created or "
                "that apply to you"
            )
            return False

        # Only the teacher who created the restriction can modify it
        if obj.teacher != request.user:
            self.message = "You can only modify restrictions you created"
            return False

        return True


class StudentRestrictionPolicy:
    """
    Policy class for student restriction operations.

    This class encapsulates all business rules for restriction operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_create_restriction(
        user: User,
        student: User,
        course: Course = None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can create a restriction.

        This method can be used by both permissions and services:
        - For permissions: returns boolean
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to create restriction
            student: Student to restrict
            course: Course to restrict student from

            raise_exception: If True, raises ServiceError instead of
                returning
                False

        Returns:
            bool: True if user can create restriction, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to create restrictions"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if user.role != "teacher":
            error_msg = "Only teachers can create restrictions"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        # Check course ownership only if course is provided
        if course and course.teacher != user:
            error_msg = "You can only create restrictions for your own courses"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if student.role != "student":
            error_msg = "Restrictions can only be applied to students"
            if raise_exception:
                raise ServiceError.bad_request(error_msg)

            return False

        # Check if exact restriction already exists
        if course:
            # For course-specific restrictions, check student + course
            duplicate_exists = StudentRestriction.objects.filter(
                student=student, course=course
            ).exists()
            error_msg = "Student is already restricted from this course"

            # Also check if global restriction exists (prevent individual)
            global_restriction_exists = StudentRestriction.objects.filter(
                student=student, course__isnull=True, teacher=user
            ).exists()
            if global_restriction_exists:
                error_msg = (
                    "You already have a global restriction on this student. "
                    "Please delete the global restriction to create "
                    "individual course restrictions."
                )
                if raise_exception:
                    raise ServiceError.conflict(error_msg)
                return False
        else:
            # For global restrictions, check student + teacher
            duplicate_exists = StudentRestriction.objects.filter(
                student=student, course__isnull=True, teacher=user
            ).exists()
            error_msg = (
                "Student already has a global restriction by this teacher"
            )

        if duplicate_exists:
            if raise_exception:
                raise ServiceError.conflict(error_msg)
            return False

        return True

    @staticmethod
    def check_can_view_restriction(
        user: User,
        restriction: StudentRestriction,

        raise_exception=False,
    ) -> bool:
        """
        Check if a user can view a restriction.

        This method can be used by both permissions and services:
        - For permissions: returns boolean
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to view restriction
            restriction: Restriction object to view

            raise_exception: If True, raises ServiceError instead of
                returning
                False

        Returns:
            bool: True if user can view, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to view restrictions"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        # Teachers can view restrictions they created
        if restriction.teacher == user:
            return True

        # Students can view restrictions applied to them
        if restriction.student == user:
            return True

        error_msg = (
            "You can only view restrictions you created or that apply to you"
        )
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_modify_restriction(
        user: User,
        restriction: StudentRestriction,

        raise_exception=False,
    ) -> bool:
        """
        Check if a user can modify a restriction.

        This method can be used by both permissions and services:
        - For permissions: returns boolean
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to modify restriction
            restriction: Restriction object to modify

            raise_exception: If True, raises ServiceError instead of
                returning
                False

        Returns:
            bool: True if user can modify, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to modify restrictions"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if user.role != "teacher":
            error_msg = "Only teachers can modify restrictions"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if restriction.teacher != user:
            error_msg = "You can only modify restrictions you created"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        return True

    @staticmethod
    def check_can_delete_restriction(
        user: User,
        restriction: StudentRestriction,

        raise_exception=False,
    ) -> bool:
        """
        Check if a user can delete a restriction.

        This method can be used by both permissions and services:
        - For permissions: returns boolean
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to delete restriction
            restriction: Restriction object to delete

            raise_exception: If True, raises ServiceError instead of
                returning
                False

        Returns:
            bool: True if user can delete, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to delete restrictions"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if user.role != "teacher":
            error_msg = "Only teachers can delete restrictions"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        if restriction.teacher != user:
            error_msg = "You can only delete restrictions you created"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)

            return False

        return True
