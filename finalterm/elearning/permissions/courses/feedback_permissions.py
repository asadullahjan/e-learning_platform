"""
Course feedback permissions.

This module contains permission classes that control access to course feedback
operations such as creating, viewing, editing, and deleting feedback.
"""

from rest_framework import permissions
from elearning.models import Course, CourseFeedback, User
from elearning.exceptions import ServiceError


class CourseFeedbackPermission(permissions.BasePermission):
    """
    Permission class for course feedback operations.

    Allows:
    - Anyone to view feedback (read-only)
    - Enrolled students to create/edit their own feedback
    - Only feedback owners can edit/delete their feedback
    """

    def has_permission(self, request, view):
        """Check if user has permission to access feedback"""
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view feedback

        # Must be logged in to create/edit
        if not request.user.is_authenticated:
            self.message = "You must be logged in to leave feedback"
            return False

        # For create/update/delete, check if user can leave feedback
        course_id = view.kwargs.get("course_pk")
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                # Use policy method that returns boolean for permissions
                # and sets appropriate error message
                if not CourseFeedbackPolicy.check_can_leave_feedback(
                    request.user, course, permission_obj=self
                ):
                    return False
            except Course.DoesNotExist:
                self.message = "Course not found"
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """Check if user can modify specific feedback object"""
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view feedback

        # Check if user can update/delete feedback and set appropriate message
        if not CourseFeedbackPolicy.check_can_update_or_delete_feedback(
            request.user, obj, permission_obj=self
        ):
            return False

        return True


class CourseFeedbackPolicy:
    """
    Policy class for course feedback operations.

    This class encapsulates all business rules for feedback operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_leave_feedback(
        user: User, course: Course, permission_obj=None, raise_exception=False
    ) -> bool:
        """
        Check if a user can leave feedback for a course.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to leave feedback
            course: Course to leave feedback for
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can leave feedback, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        # Check if course is published
        if not course.published_at:
            error_msg = "Cannot leave feedback for unpublished course"
            if raise_exception:
                raise ServiceError.bad_request(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Check if user is enrolled in the course
        enrollments_exist = course.enrollments.filter(
            user=user, is_active=True
        ).exists()
        if not enrollments_exist:
            error_msg = "You must be enrolled in this course to leave feedback"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        # Check if user already left feedback
        feedback_exists = CourseFeedback.objects.filter(
            user=user, course=course
        ).exists()
        if feedback_exists:
            error_msg = "You have already left feedback for this course"
            if raise_exception:
                raise ServiceError.conflict(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True

    @staticmethod
    def check_can_update_or_delete_feedback(
        user: User,
        feedback: CourseFeedback,
        permission_obj=None,
        raise_exception=False,
    ) -> bool:
        """
        Check if a user can update or delete feedback.

        This method can be used by both permissions and services:
        - For permissions: returns boolean and sets custom message
        - For services: raises ServiceError with detailed message

        Args:
            user: User attempting to modify feedback
            feedback: Feedback instance to modify
            permission_obj: Permission object to set custom messages (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can modify feedback, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if user != feedback.user:
            error_msg = "You can only edit or delete your own feedback"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            if permission_obj:
                permission_obj.message = error_msg
            return False

        return True

    @staticmethod
    def check_can_view_feedback(
        user: User, feedback: CourseFeedback, raise_exception: bool = False
    ) -> bool:
        """
        Check if a user can view feedback (currently allows everyone).

        Args:
            user: User attempting to view feedback
            feedback: Feedback object to view
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: Always True (anyone can view feedback)
        """
        # Currently anyone can view feedback
        # Add restrictions here if needed in the future
        return True
