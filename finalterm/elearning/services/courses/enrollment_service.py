from elearning.models import Enrollment, Course, User
from elearning.services.notification_service import NotificationService
from elearning.exceptions import ServiceError
from elearning.permissions.courses.enrollment_permissions import (
    EnrollmentPolicy,
)


class EnrollmentService:
    """
    Service for managing course enrollments.
    """

    @staticmethod
    def check_can_enroll(student: User, course: Course) -> bool:
        """
        Check if a student can enroll in a course.

        This method provides early permission checking that can be used by
        both permissions classes and the service itself.

        Args:
            student: User attempting to enroll
            course: Course to enroll in

        Returns:
            bool: True if student can enroll, False otherwise
        """
        return EnrollmentPolicy.check_can_enroll(student, course)

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
        EnrollmentPolicy.check_can_enroll(
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
                # Check if student is restricted before reactivating
                from elearning.services.courses.student_restriction_service import (
                    StudentRestrictionService,
                )

                restriction_info = (
                    StudentRestrictionService.get_restriction_info(
                        student, course
                    )
                )

                if restriction_info["is_restricted"]:
                    if (
                        restriction_info["restriction_type"]
                        == "teacher_all_courses"
                    ):
                        error_msg = (
                            f"You are restricted from accessing all courses by "
                            f"{restriction_info['teacher']}. "
                            f"Reason: {restriction_info['reason']}"
                        )
                    else:  # course-specific
                        error_msg = (
                            f"You are restricted from accessing this course. "
                            f"Reason: {restriction_info['reason']}"
                        )
                    raise ServiceError.permission_denied(error_msg)

                # Reactivate existing enrollment
                existing_enrollment.is_active = True
                existing_enrollment.save()
                return existing_enrollment

        # Check if student is restricted before creating new enrollment
        from elearning.services.courses.student_restriction_service import (
            StudentRestrictionService,
        )

        restriction_info = StudentRestrictionService.get_restriction_info(
            student, course
        )

        if restriction_info["is_restricted"]:
            if restriction_info["restriction_type"] == "teacher_all_courses":
                error_msg = (
                    f"You are restricted from accessing all courses by "
                    f"{restriction_info['teacher']}. "
                    f"Reason: {restriction_info['reason']}"
                )
            else:  # course-specific
                error_msg = (
                    f"You are restricted from accessing this course. "
                    f"Reason: {restriction_info['reason']}"
                )
            raise ServiceError.permission_denied(error_msg)

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
            EnrollmentPolicy.check_can_unenroll(
                student, enrollment, raise_exception=True
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

    @staticmethod
    def get_enrollment_with_permission_check(enrollment_id: int, user: User):
        """Get enrollment with permission check"""
        try:
            enrollment = Enrollment.objects.select_related(
                "course", "course__teacher", "user"
            ).get(id=enrollment_id)
            # Check if user can view this enrollment
            EnrollmentPolicy.check_can_view_enrollment(
                user, enrollment, raise_exception=True
            )
            return enrollment
        except Enrollment.DoesNotExist:
            raise ServiceError.not_found("Enrollment not found")

    @staticmethod
    def modify_enrollment(enrollment: Enrollment, user: User, **kwargs):
        """Modify enrollment with permission check and restriction validation"""
        # Check if user can modify this enrollment
        EnrollmentPolicy.check_can_modify_enrollment(
            user, enrollment, raise_exception=True
        )

        # If activating enrollment, check for restrictions
        if kwargs.get("is_active") is True:
            from elearning.services.courses.student_restriction_service import (
                StudentRestrictionService,
            )

            restriction_info = StudentRestrictionService.get_restriction_info(
                enrollment.user, enrollment.course
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
