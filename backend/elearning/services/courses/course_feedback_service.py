from django.db import transaction
from elearning.models import CourseFeedback, Course, User
from elearning.exceptions import ServiceError
from elearning.permissions.courses import (
    CourseFeedbackPolicy,
)
from elearning.services.courses.course_service import CourseService


class CourseFeedbackService:
    """
    Service for managing course feedback operations and business logic.

    This service encapsulates all business logic related to course feedback
    including:
    - Feedback creation and validation
    - Feedback modification and deletion
    - Permission checking for feedback operations

    The service follows the single responsibility principle and provides
    a clean interface for views to interact with feedback-related operations.
    All business rules are centralized here to ensure consistency.
    
    Note: This service does NOT check student restrictions directly. Access
    is determined by enrollment status (enrollment.is_active), which is
    automatically managed by the restriction service.
    """

    @staticmethod
    @transaction.atomic
    def create_feedback(user: User, course: Course, rating: int, text: str):
        """
        Create course feedback for a user.

        This method creates feedback after validating all business rules.
        It ensures data integrity and provides meaningful error messages
        when validation fails.

        Args:
            user: User creating the feedback
            course: Course to leave feedback for
            rating: Rating value (1-5)
            text: Feedback text

        Returns:
            CourseFeedback instance

        Raises:
            ServiceError: If validation fails (course unpublished, not
                         enrolled, or duplicate feedback)

        Example:
            >>> feedback = CourseFeedbackService.create_feedback(
            ...     user, course, 5, "Excellent course!"
            ... )
            >>> print(f"Created feedback: {feedback.rating}/5")
        """
        # Use the permission policy for validation
        CourseFeedbackPolicy.check_can_leave_feedback(
            user, course, raise_exception=True
        )

        # Create the feedback
        feedback = CourseFeedback.objects.create(
            user=user, course=course, rating=rating, text=text
        )

        return feedback

    @staticmethod
    @transaction.atomic
    def update_feedback(feedback: CourseFeedback, user: User, **data):
        """
        Update existing feedback.

        This method allows users to modify their own feedback while
        ensuring only the feedback owner can make changes.

        Args:
            feedback: CourseFeedback instance to update
            user: User making the update
            **data: Fields to update (rating, text)

        Returns:
            Updated CourseFeedback instance

        Raises:
            ServiceError: If user doesn't own the feedback

        Example:
            >>> updated_feedback = CourseFeedbackService.update_feedback(
            ...     feedback, user, rating=4, text="Updated review"
            ... )
            >>> print(f"Updated rating: {updated_feedback.rating}")
        """
        # Use the permission policy for validation
        CourseFeedbackPolicy.check_can_update_or_delete_feedback(
            user, feedback, raise_exception=True
        )

        for field, value in data.items():
            setattr(feedback, field, value)

        feedback.save()
        return feedback

    @staticmethod
    def delete_feedback(feedback: CourseFeedback, user: User):
        """
        Delete feedback.

        This method allows users to remove their own feedback while
        ensuring only the feedback owner can delete it.

        Args:
            feedback: CourseFeedback instance to delete
            user: User making the deletion

        Raises:
            ServiceError: If user doesn't own the feedback

        Example:
            >>> CourseFeedbackService.delete_feedback(feedback, user)
            >>> print("Feedback deleted successfully")
        """
        # Use the permission policy for validation
        CourseFeedbackPolicy.check_can_update_or_delete_feedback(
            user, feedback, raise_exception=True
        )

        feedback.delete()

    @staticmethod
    def get_course_feedback(course: Course):
        """
        Get all feedback for a course.

        This method retrieves all feedback for a specific course,
        ordered by creation date (newest first).

        Args:
            course: Course instance

        Returns:
            QuerySet of feedback ordered by creation date

        Example:
            >>> feedback_list = CourseFeedbackService.get_course_feedback(
            ...     course
            ... )
            >>> for feedback in feedback_list:
            ...     print(f"{feedback.user.username}: {feedback.rating}/5")
        """
        return CourseFeedback.objects.filter(course=course).order_by(
            "-created_at"
        )

    @staticmethod
    def get_feedback_with_permission_check(feedback_id: int, user: User):
        """
        Get feedback with permission check including course access validation
        """
        try:
            feedback = CourseFeedback.objects.get(id=feedback_id)

            # First check if user can access the course this feedback
            # belongs to
            CourseService.get_course_with_permission_check(
                feedback.course.id, user
            )

            # Then check if user can view this specific feedback
            CourseFeedbackPolicy.check_can_view_feedback(
                user, feedback, raise_exception=True
            )

            return feedback
        except CourseFeedback.DoesNotExist:
            raise ServiceError.not_found("Feedback not found")

    @staticmethod
    def get_user_feedback(user: User):
        """
        Get all feedback by a user.

        This method retrieves all feedback created by a specific user,
        ordered by creation date (newest first).

        Args:
            user: User instance

        Returns:
            QuerySet of feedback ordered by creation date

        Example:
            >>> user_feedback = CourseFeedbackService.get_user_feedback(user)
            >>> print(f"User has left {user_feedback.count()} feedback")
        """
        return CourseFeedback.objects.filter(user=user).order_by("-created_at")
