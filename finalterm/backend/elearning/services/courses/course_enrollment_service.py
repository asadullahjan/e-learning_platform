from elearning.models import Enrollment, Course, User
from elearning.services.notification_service import NotificationService
from elearning.exceptions import ServiceError
from elearning.permissions.courses import (
    CourseEnrollmentPolicy,
)
from django.utils import timezone


class CourseEnrollmentService:
    """
    Service for managing course enrollments.

    This service handles all business logic related to course enrollments:
    - Creating and managing enrollments
    - Checking restrictions before enrollment operations
    - Managing enrollment lifecycle

    Note: This is the ONLY service that should check student restrictions.
    All other services should check enrollment.is_active status instead.
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
        # Use the permission policy for validation
        CourseEnrollmentPolicy.check_can_enroll(
            student, course, raise_exception=True
        )

        # Check if already enrolled
        existing_enrollment = (
            Enrollment.objects.select_related(
                "course", "course__teacher", "user"
            )
            .filter(course=course, user=student)
            .first()
        )

        if existing_enrollment:
            if existing_enrollment.is_active:
                raise ServiceError.conflict(
                    "Student is already enrolled in this course"
                )
            else:
                # Reactivate existing enrollment
                existing_enrollment.is_active = True
                existing_enrollment.unenrolled_at = None
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
            enrollment = Enrollment.objects.select_related(
                "course", "course__teacher", "user"
            ).get(course=course, user=student, is_active=True)

            # Check if user can unenroll
            CourseEnrollmentPolicy.check_can_unenroll(
                student, enrollment, raise_exception=True
            )

            enrollment.is_active = False
            enrollment.unenrolled_at = timezone.now()
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

    @staticmethod
    def get_enrollment_with_permission_check(enrollment_id: int, user: User):
        """Get enrollment with permission check"""
        try:
            enrollment = Enrollment.objects.select_related(
                "course", "course__teacher", "user"
            ).get(id=enrollment_id)
            # Check if user can view this enrollment
            CourseEnrollmentPolicy.check_can_view_enrollment(
                user, enrollment, raise_exception=True
            )
            return enrollment
        except Enrollment.DoesNotExist:
            raise ServiceError.not_found("Enrollment not found")

    @staticmethod
    def modify_enrollment(enrollment: Enrollment, user: User, **kwargs):
        """
        Modify enrollment with permission check and restriction validation
        """
        # Check if user can modify this enrollment
        CourseEnrollmentPolicy.check_can_modify_enrollment(
            user, enrollment, raise_exception=True
        )

        # If activating enrollment, check for restrictions
        if kwargs.get("is_active") is True:
            from elearning.services.courses import (
                CourseStudentRestrictionService,
            )

            restriction_info = (
                CourseStudentRestrictionService.get_restriction_info(
                    enrollment.user, enrollment.course
                )
            )

            if restriction_info["is_restricted"]:
                if (
                    restriction_info["restriction_type"]
                    == "teacher_all_courses"
                ):
                    error_msg = (
                        f"User is restricted from accessing all courses by "
                        f"{restriction_info['teacher']}. "
                        f"Reason: {restriction_info['reason']}"
                    )
                else:  # course-specific
                    error_msg = (
                        f"User is restricted from accessing this course. "
                        f"Reason: {restriction_info['reason']}"
                    )
                raise ServiceError.permission_denied(error_msg)

        # Update enrollment fields
        for field, value in kwargs.items():
            if hasattr(enrollment, field):
                setattr(enrollment, field, value)

        enrollment.save()
        return enrollment

    @staticmethod
    def get_enrollments_for_course(course: Course, user: User):
        """Get enrollments for a course with permission filtering"""
        # Teachers see all enrollments for their courses
        if user.is_authenticated and course.teacher == user:
            return Enrollment.objects.select_related(
                "user", "course", "course__teacher"
            ).filter(course=course)

        # Students see only their own enrollment for this course
        if user.is_authenticated:
            return Enrollment.objects.select_related(
                "user", "course", "course__teacher"
            ).filter(course=course, user=user)

        # Unauthenticated users see nothing
        return Enrollment.objects.none()

    @staticmethod
    def is_student_enrolled_and_active(student: User, course: Course) -> bool:
        """
        Check if a student is enrolled and has active enrollment for a course.
        This is the single source of truth for course access.

        Args:
            student: Student user to check
            course: Course to check enrollment for

        Returns:
            bool: True if student has active enrollment, False otherwise
        """
        return course.enrollments.filter(user=student, is_active=True).exists()

    @staticmethod
    def get_active_enrollment(student: User, course: Course):
        """
        Get the active enrollment for a student in a course.

        Args:
            student: Student user
            course: Course to get enrollment for

        Returns:
            Enrollment instance if exists and active, None otherwise
        """
        try:
            return course.enrollments.get(user=student, is_active=True)
        except Enrollment.DoesNotExist:
            return None
