from elearning.models import Enrollment, Course, User
from elearning.services.notification_service import NotificationService
from elearning.exceptions import ServiceError


class EnrollmentService:
    """
    Service for managing course enrollments.
    """

    @staticmethod
    def enroll_student(course: Course, student: User):
        """
        Enroll a student in a course.

        Args:
            course: Course instance
            student: User instance (student)

        Returns:
            Enrollment instance
        """
        # Check if already enrolled
        existing_enrollment = Enrollment.objects.filter(
            course=course, user=student
        ).first()

        if existing_enrollment:
            if existing_enrollment.is_active:
                raise ServiceError.conflict(
                    "Student is already enrolled in this course"
                )
            else:
                # Reactivate existing enrollment
                existing_enrollment.is_active = True
                existing_enrollment.save()
                return existing_enrollment

        # Create new enrollment
        enrollment = Enrollment.objects.create(
            course=course, user=student, is_active=True
        )

        # Notify teacher about new enrollment
        NotificationService.create_notifications_and_send(
            user_ids=[course.teacher.id],
            title="New Student Enrollment",
            message=f"{student.username} has enrolled in {course.title}",
            action_url=f"/courses/{course.id}/enrollments",
        )

        return enrollment

    @staticmethod
    def unenroll_student(course: Course, student: User):
        """
        Unenroll a student from a course.

        Args:
            course: Course instance
            student: User instance (student)

        Returns:
            bool: True if unenrolled, False if not enrolled
        """
        try:
            enrollment = Enrollment.objects.get(
                course=course, user=student, is_active=True
            )

            enrollment.is_active = False
            enrollment.save()

            # Notify teacher about unenrollment
            message = f"{student.username} has unenrolled from {course.title}"
            NotificationService.create_notifications_and_send(
                user_ids=[course.teacher.id],
                title="Student Unenrolled",
                message=message,
                action_url=f"/courses/{course.id}/enrollments",
            )

            return True

        except Enrollment.DoesNotExist:
            return False
