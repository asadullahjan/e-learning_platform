from django.utils import timezone
from elearning.models import (
    StudentRestriction,
    Enrollment,
    User,
    Course,
    ChatRoom,
    ChatParticipant,
)
from elearning.services.notification_service import NotificationService
from elearning.exceptions import ServiceError
from elearning.permissions.courses import (
    CourseStudentRestrictionPolicy,
)


class CourseStudentRestrictionService:
    """
    Service for managing student restrictions.

    This service handles all business logic related to student restrictions:
    - Creating and managing restrictions
    - Applying restriction effects to enrollments
    - Managing restriction lifecycle

    Note: This service does NOT handle access checking. Access is determined
    by enrollment status (enrollment.is_active), which is automatically
    managed when restrictions are created/deleted.
    """

    @staticmethod
    def create_restriction(teacher, student, course=None, reason=""):
        """
        Create a new student restriction.

        Args:
            teacher: User object (must be a teacher)
            student: User object of the student to restrict
            course: Optional Course object for course-specific restriction
            reason: Optional reason for the restriction

        Returns:
            StudentRestriction instance

        Raises:
            ServiceError: If validation fails
        """
        # Use the permission policy for validation
        CourseStudentRestrictionPolicy.check_can_create_restriction(
            teacher, student, course, raise_exception=True
        )

        # Handle overlapping restrictions
        if not course:
            # Creating global restriction - remove existing course-specific
            StudentRestriction.objects.filter(
                teacher=teacher, student=student, course__isnull=False
            ).delete()
        else:
            # Creating course-specific restriction - check if global exists
            global_restriction_exists = StudentRestriction.objects.filter(
                teacher=teacher, student=student, course__isnull=True
            ).exists()

            if global_restriction_exists:
                raise ServiceError.conflict(
                    "You already have a global restriction on this student. "
                    "Please delete the global restriction to create "
                    "individual course restrictions."
                )

        # Create the restriction
        restriction = StudentRestriction.objects.create(
            teacher=teacher,
            student=student,
            course=course,
            reason=reason,
        )

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
            user_ids=[student.id],
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
        CourseStudentRestrictionPolicy.check_can_delete_restriction(
            user, restriction, raise_exception=True
        )

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

    # CALLED BY SIGNAL
    @staticmethod
    def apply_restriction_effects(restriction):
        """
        Apply a restriction:
        - Deactivate enrollments
        - Deactivate chat participants
        """
        print(
            "apply_restriction_effects",
            restriction.course,
            restriction.student,
        )
        if restriction.course:
            # Course-specific restriction
            enrollments = Enrollment.objects.filter(
                course=restriction.course,
                user=restriction.student,
                is_active=True,
            )
        else:
            # Teacher all-courses restriction
            teacher_courses = Course.objects.filter(
                teacher=restriction.teacher
            )
            enrollments = Enrollment.objects.filter(
                course__in=teacher_courses,
                user=restriction.student,
                is_active=True,
            )

        # Get chat rooms ids before updating enrollments
        # .update updates the queryset in place, so we need to get the ids
        chat_rooms_ids = [e.course.id for e in enrollments]

        # Bulk update enrollments
        enrollments.update(is_active=False, unenrolled_at=timezone.now())

        # Bulk update corresponding chat participants
        chatrooms = ChatRoom.objects.filter(id__in=chat_rooms_ids)

        ChatParticipant.objects.filter(
            chat_room__in=chatrooms, user=restriction.student, is_active=True
        ).update(is_active=False)

    # CALLED BY SIGNAL
    @staticmethod
    def remove_restriction_effects(restriction):
        """
        Remove a restriction:
        - Reactivate enrollments if no other restrictions apply
        - Reactivate chat participants
        """
        if restriction.course:
            # Course-specific restriction
            if not CourseStudentRestrictionPolicy.is_restricted(
                restriction.student, restriction.course
            ):
                enrollments = Enrollment.objects.filter(
                    course=restriction.course,
                    user=restriction.student,
                    is_active=False,
                )
            else:
                return
        else:
            # Teacher all-courses restriction
            teacher_courses = Course.objects.filter(
                teacher=restriction.teacher
            )
            enrollments = Enrollment.objects.filter(
                course__in=teacher_courses,
                user=restriction.student,
                is_active=False,
            )

        # Bulk update enrollments
        enrollments.update(is_active=True, unenrolled_at=None)

        # Bulk update corresponding chat participants
        chatrooms = ChatRoom.objects.filter(
            course__in=[e.course for e in enrollments], chat_type="course"
        )
        ChatParticipant.objects.filter(
            chat_room__in=chatrooms, user=restriction.student, is_active=False
        ).update(is_active=True)

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

        return StudentRestriction.objects.filter(
            teacher=teacher
        ).select_related("student", "course")

    @staticmethod
    def get_restriction_with_permission_check(restriction_id: int, user: User):
        """Get restriction with permission check"""
        try:
            restriction = StudentRestriction.objects.select_related(
                "student", "course"
            ).get(id=restriction_id)

            can_view = (
                CourseStudentRestrictionPolicy.check_can_view_restriction(
                    user, restriction, raise_exception=False
                )
            )
            if not can_view:
                raise ServiceError.not_found("Restriction not found")
            return restriction
        except StudentRestriction.DoesNotExist:
            raise ServiceError.not_found("Restriction not found")
