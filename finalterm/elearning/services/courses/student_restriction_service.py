from elearning.models import (
    StudentRestriction,
    Enrollment,
    ChatParticipant,
    User,
    Course,
)
from elearning.services.notification_service import NotificationService
from elearning.exceptions import ServiceError
from elearning.permissions.courses.restriction_permissions import (
    StudentRestrictionPolicy,
)


class StudentRestrictionService:
    """
    Service for managing student restrictions.
    """

    @staticmethod
    def check_can_create_restriction(
        teacher, student_id, course_id=None
    ) -> bool:
        """
        Check if a teacher can create a restriction for a student.

        This method provides early permission checking that can be used by
        both permissions classes and the service itself.

        Args:
            teacher: User attempting to create restriction
            student_id: ID of the student to restrict
            course_id: Optional course ID for course-specific restriction

        Returns:
            bool: True if teacher can create restriction, False otherwise
        """
        try:
            student = User.objects.get(id=student_id)
            course = None
            if course_id:
                course = Course.objects.get(id=course_id)
            return StudentRestrictionPolicy.check_can_create_restriction(
                teacher, student, course
            )
        except (User.DoesNotExist, Course.DoesNotExist):
            return False

    @staticmethod
    def create_restriction(teacher, student_id, course_id=None, reason=""):
        """
        Create a new student restriction.

        Args:
            teacher: User object (must be a teacher)
            student_id: ID of the student to restrict
            course_id: Optional course ID for course-specific restriction
            reason: Optional reason for the restriction

        Returns:
            StudentRestriction instance

        Raises:
            ServiceError: If validation fails
        """
        try:
            student = User.objects.get(id=student_id)
            course = None
            if course_id:
                course = Course.objects.get(id=course_id)

            # Use the permission policy for validation
            StudentRestrictionPolicy.check_can_create_restriction(
                teacher, student, course, raise_exception=True
            )
        except User.DoesNotExist:
            raise ServiceError.not_found("Student not found")
        except Course.DoesNotExist:
            raise ServiceError.not_found("Course not found")

        # Create the restriction
        restriction = StudentRestriction.objects.create(
            teacher=teacher,
            student_id=student_id,
            course_id=course_id,
            reason=reason,
        )

        # Apply the restriction effects
        StudentRestrictionService._apply_restriction_effects(restriction)

        # Notify student about restriction
        reason_text = reason or "No reason provided"

        if restriction.course:
            # Course-specific restriction
            message = (
                f"You have been restricted from accessing "
                f"{restriction.course.title} by "
                f"{restriction.teacher.username}. Reason: {reason_text}"
            )
            action_url = f"/courses/{restriction.course.id}"
            title = "Course Access Restricted"
        else:
            # All courses restriction
            message = (
                f"You have been restricted from accessing all courses "
                f"by {restriction.teacher.username}. Reason: {reason_text}"
            )
            action_url = "/courses"
            title = "All Courses Access Restricted"

        NotificationService.create_notifications_and_send(
            user_ids=[student_id],
            title=title,
            message=message,
            action_url=action_url,
        )

        return restriction

    @staticmethod
    def delete_restriction(restriction, user):
        """
        Delete a student restriction and restore access.

        Args:
            restriction: StudentRestriction instance to delete
            user: User attempting to delete the restriction
        """
        # Check if user can delete this restriction
        StudentRestrictionPolicy.check_can_delete_restriction(
            user, restriction, raise_exception=True
        )

        # Remove restriction effects before deleting
        StudentRestrictionService._remove_restriction_effects(restriction)

        # Notify student that restriction has been removed
        if restriction.course:
            message = (
                f"Your access to {restriction.course.title} has been restored "
                f"by {restriction.teacher.username}."
            )
            action_url = f"/courses/{restriction.course.id}"
            title = "Course Access Restored"
        else:
            message = (
                f"Your access to all courses has been restored "
                f"by {restriction.teacher.username}."
            )
            action_url = "/courses"
            title = "All Courses Access Restored"

        NotificationService.create_notifications_and_send(
            user_ids=[restriction.student.id],
            title=title,
            message=message,
            action_url=action_url,
        )

        # Delete the restriction
        restriction.delete()

    @staticmethod
    def _apply_restriction_effects(restriction):
        """
        Apply the effects of a restriction.
        - Deactivate course enrollment if course-specific
        - Remove from course chat if applicable
        """
        if restriction.course:
            # Deactivate course enrollment
            Enrollment.objects.filter(
                course=restriction.course,
                user=restriction.student,
                is_active=True,
            ).update(is_active=False)

            # Remove from course chat if exists
            try:
                chat_participant = ChatParticipant.objects.get(
                    chat_room__course=restriction.course,
                    user=restriction.student,
                )
                chat_participant.is_active = False
                chat_participant.save()
            except ChatParticipant.DoesNotExist:
                pass  # Not in course chat

    @staticmethod
    def _remove_restriction_effects(restriction):
        """
        Remove the effects of a restriction.
        - Reactivate course enrollment if course-specific
        - Restore course chat access if applicable
        """
        if restriction.course:
            # Reactivate course enrollment
            Enrollment.objects.filter(
                course=restriction.course,
                user=restriction.student,
                is_active=False,
            ).update(is_active=True)

            # Restore course chat access if exists
            try:
                chat_participant = ChatParticipant.objects.get(
                    chat_room__course=restriction.course,
                    user=restriction.student,
                )
                chat_participant.is_active = True
                chat_participant.save()
            except ChatParticipant.DoesNotExist:
                pass  # Not in course chat

    @staticmethod
    def get_teacher_restrictions(teacher):
        """
        Get all restrictions created by a teacher.

        Args:
            teacher: User object (must be a teacher)

        Returns:
            QuerySet of StudentRestriction instances
        """
        if teacher.role != "teacher":
            return StudentRestriction.objects.none()

        return StudentRestriction.objects.filter(teacher=teacher)

    @staticmethod
    def is_student_restricted(student, teacher, course=None):
        """
        Check if a student is restricted by a specific teacher.

        Args:
            student: User object (student)
            teacher: User object (teacher)
            course: Optional course object

        Returns:
            bool: True if restricted, False otherwise
        """
        if course:
            return StudentRestriction.objects.filter(
                teacher=teacher, student=student, course=course
            ).exists()
        else:
            # Check for teacher-level restriction (no course specified)
            return StudentRestriction.objects.filter(
                teacher=teacher, student=student, course__isnull=True
            ).exists()

    @staticmethod
    def get_restriction_with_permission_check(restriction_id: int, user: User):
        """Get restriction with permission check"""
        try:
            restriction = StudentRestriction.objects.get(id=restriction_id)
            # Check if user can view this restriction
            StudentRestrictionPolicy.check_can_view_restriction(
                user, restriction, raise_exception=True
            )
            return restriction
        except StudentRestriction.DoesNotExist:
            raise ServiceError.not_found("Restriction not found")

    @staticmethod
    def modify_restriction(
        restriction: StudentRestriction, user: User, **kwargs
    ):
        """Modify restriction with permission check"""
        # Check if user can modify this restriction
        StudentRestrictionPolicy.check_can_modify_restriction(
            user, restriction, raise_exception=True
        )

        # Update restriction fields
        for field, value in kwargs.items():
            if hasattr(restriction, field):
                setattr(restriction, field, value)

        restriction.save()
        return restriction
