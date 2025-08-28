from django.core.cache import cache
from django.db import models
from django.utils import timezone
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
    def get_restricted_courses_for_student(student: User):
        """
        Get all course IDs that a student is restricted from accessing.
        Optimized version with single query and select_related.

        This handles both:
        - Specific course restrictions
        - All-courses restrictions by teachers (gets all courses by teachers)

        Returns:
            set: Set of course IDs the student cannot access
        """
        restricted_course_ids = set()

        # Single optimized query to get all restrictions for this student
        restrictions = StudentRestriction.objects.select_related(
            "course", "course__teacher", "teacher"
        ).filter(student=student)

        for restriction in restrictions:
            if restriction.course:
                # Specific course restriction
                restricted_course_ids.add(restriction.course.id)
            else:
                # Teacher all-courses restriction - get all courses by teacher
                teacher_course_ids = Course.objects.filter(
                    teacher=restriction.teacher
                ).values_list("id", flat=True)
                restricted_course_ids.update(teacher_course_ids)

        return restricted_course_ids

    @staticmethod
    def is_student_restricted(
        student: User, teacher: User, course: Course = None
    ) -> bool:
        """
        Check if a student is restricted by a teacher for a course or globally.

        Args:
            student: Student user to check restrictions for
            teacher: Teacher user checking the restrictions
            course: Optional course to check course-specific restrictions

        Returns:
            bool: True if student is restricted, False otherwise
        """
        restriction_info = StudentRestrictionService.get_restriction_info(
            student, course
        )
        return restriction_info["is_restricted"]

    @staticmethod
    def get_restriction_info(student: User, course: Course = None) -> dict:
        """
        Get detailed restriction information for a student.
        Optimized version with caching and single query.

        Args:
            student: Student user to check restrictions for
            course: Optional course to check course-specific restrictions

        Returns:
            dict: Restriction information including reason if restricted
        """
        if not course:
            return {
                "is_restricted": False,
                "restriction_type": None,
                "reason": None,
            }

        # Use optimized single query with select_related
        restriction = (
            StudentRestriction.objects.select_related(
                "teacher", "course", "course__teacher"
            )
            .filter(student=student)
            .filter(
                models.Q(course=course)
                | models.Q(teacher=course.teacher, course__isnull=True)
            )
            .order_by("course_id")  # Prioritize course-specific restrictions
            .first()
        )

        if restriction:
            if restriction.course:
                restriction_type = "course"
            else:
                restriction_type = "teacher_all_courses"

            return {
                "is_restricted": True,
                "restriction_type": restriction_type,
                "reason": restriction.reason or "No reason provided",
                "teacher": restriction.teacher.username,
                "created_at": restriction.created_at,
                "course": course.title,
            }

        return {
            "is_restricted": False,
            "restriction_type": None,
            "reason": None,
        }

    @staticmethod
    def get_restriction_info_cached(
        student: User, course: Course = None
    ) -> dict:
        """
        Get restriction info with caching for better performance.

        Args:
            student: Student user to check restrictions for
            course: Optional course to check course-specific restrictions

        Returns:
            dict: Restriction information including reason if restricted
        """
        if not course:
            return {
                "is_restricted": False,
                "restriction_type": None,
                "reason": None,
            }

        # Create cache key
        cache_key = f"restriction_info_{student.id}_{course.id}"

        # Try to get from cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Get from database if not cached
        result = StudentRestrictionService.get_restriction_info(
            student, course
        )

        # Cache for 5 minutes (300 seconds)
        cache.set(cache_key, result, 300)

        return result

    @staticmethod
    def bulk_check_restrictions(students: list, courses: list = None) -> dict:
        """
        Bulk check restrictions for multiple students and courses.
        Much more efficient than individual checks.

        Args:
            students: List of User objects to check
            courses: Optional list of Course objects to check

        Returns:
            dict: Nested dict with structure
            {student_id: {course_id: restriction_info}}
        """
        if not students:
            return {}

        student_ids = [s.id for s in students]
        course_ids = [c.id for c in courses] if courses else []

        # Single query to get all relevant restrictions
        restrictions_qs = StudentRestriction.objects.select_related(
            "student", "teacher", "course", "course__teacher"
        ).filter(student_id__in=student_ids)

        # If courses provided, filter by them or their teachers
        if courses:
            course_teacher_ids = [c.teacher_id for c in courses]
            restrictions_qs = restrictions_qs.filter(
                models.Q(course_id__in=course_ids)
                | models.Q(
                    teacher_id__in=course_teacher_ids, course__isnull=True
                )
            )

        # Build result dictionary
        result = {}
        for student in students:
            result[student.id] = {}
            if courses:
                for course in courses:
                    result[student.id][course.id] = {
                        "is_restricted": False,
                        "restriction_type": None,
                        "reason": None,
                    }

        # Process restrictions
        for restriction in restrictions_qs:
            student_id = restriction.student_id

            if restriction.course_id and restriction.course_id in course_ids:
                # Course-specific restriction
                result[student_id][restriction.course_id] = {
                    "is_restricted": True,
                    "restriction_type": "course",
                    "reason": restriction.reason or "No reason provided",
                    "teacher": restriction.teacher.username,
                    "created_at": restriction.created_at,
                }
            elif not restriction.course_id and courses:
                # Teacher all-courses restriction - apply to all courses
                for course in courses:
                    if course.teacher_id == restriction.teacher_id:
                        result[student_id][course.id] = {
                            "is_restricted": True,
                            "restriction_type": "teacher_all_courses",
                            "reason": (
                                restriction.reason or "No reason provided"
                            ),
                            "teacher": restriction.teacher.username,
                            "created_at": restriction.created_at,
                        }

        return result

    @staticmethod
    def invalidate_restriction_cache(student_id: int, course_id: int = None):
        """
        Invalidate restriction cache when restrictions are
        created/updated/deleted.

        Args:
            student_id: ID of the student
            course_id: Optional course ID for course-specific
            cache invalidation
        """
        if course_id:
            # Invalidate specific course cache
            cache_key = f"restriction_info_{student_id}_{course_id}"
            cache.delete(cache_key)
        else:
            # Invalidate all restriction caches for this student
            # This is a simple approach - in production you might want to
            # track cache keys
            # Note: Django cache doesn't support pattern deletion by default
            # You might need to implement this with Redis or similar
            pass

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

        # Handle overlapping restrictions
        if not course_id:
            # Creating global restriction - remove existing course-specific
            StudentRestriction.objects.filter(
                teacher=teacher, student_id=student_id, course__isnull=False
            ).delete()
        else:
            # Creating course-specific restriction - check if global exists
            global_restriction_exists = StudentRestriction.objects.filter(
                teacher=teacher, student_id=student_id, course__isnull=True
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
            student_id=student_id,
            course_id=course_id,
            reason=reason,
        )

        # Invalidate cache for this student/course combination
        StudentRestrictionService.invalidate_restriction_cache(
            student_id, course_id
        )

        # Note: Restriction effects are now applied automatically via signals

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

        # Store IDs for cache invalidation before deletion
        student_id = restriction.student_id
        course_id = restriction.course_id

        # Note: Restriction effects are now removed automatically via signals

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

        # Invalidate cache after deletion
        StudentRestrictionService.invalidate_restriction_cache(
            student_id, course_id
        )

    @staticmethod
    def _apply_restriction_effects(restriction):
        """
        Apply the effects of a restriction.
        - Deactivate course enrollment if course-specific
        - Deactivate chat participants for course chats if applicable
        - For teacher all-courses restrictions, deactivate all enrollments
        and chat participants for that teacher's courses
        """
        if restriction.course:
            # Course-specific restriction
            # Deactivate course enrollment
            Enrollment.objects.filter(
                course=restriction.course,
                user=restriction.student,
                is_active=True,
            ).update(is_active=False, unenrolled_at=timezone.now())

            # Deactivate chat participants for course chat
            ChatParticipant.objects.filter(
                chat_room__course=restriction.course,
                chat_room__chat_type="course",
                user=restriction.student,
                is_active=True,
            ).update(is_active=False)
        else:
            # Teacher all-courses restriction
            # Get all courses by this teacher
            teacher_courses = Course.objects.select_related("teacher").filter(
                teacher=restriction.teacher
            )

            # Deactivate all enrollments for this teacher's courses
            Enrollment.objects.filter(
                course__in=teacher_courses,
                user=restriction.student,
                is_active=True,
            ).update(is_active=False, unenrolled_at=timezone.now())

            # Deactivate all chat participants for this teacher's course chats
            ChatParticipant.objects.filter(
                chat_room__course__in=teacher_courses,
                chat_room__chat_type="course",
                user=restriction.student,
                is_active=True,
            ).update(is_active=False)

    @staticmethod
    def _remove_restriction_effects(restriction):
        """
        Remove the effects of a restriction.
        - Only reactivate if no other restrictions still apply
        - Check for remaining restrictions before reactivating
        - For teacher all-courses restrictions, reactivate all enrollments
        and chat participants for that teacher's courses
        """
        if restriction.course:
            # Course-specific restriction
            # Check if student is still restricted for this course
            remaining_restriction_info = (
                StudentRestrictionService.get_restriction_info(
                    restriction.student, restriction.course
                )
            )

            # Only reactivate if no other restrictions apply
            if not remaining_restriction_info["is_restricted"]:
                # Reactivate course enrollment
                Enrollment.objects.filter(
                    course=restriction.course,
                    user=restriction.student,
                    is_active=False,
                ).update(is_active=True, unenrolled_at=None)

                # Restore course chat access if exists
                ChatParticipant.objects.filter(
                    chat_room__course=restriction.course,
                    chat_room__chat_type="course",
                    user=restriction.student,
                    is_active=False,
                ).update(is_active=True)
        else:
            # Teacher all-courses restriction
            # Get all courses by this teacher
            teacher_courses = Course.objects.select_related("teacher").filter(
                teacher=restriction.teacher
            )

            # Since we prevent overlapping restrictions, we can safely reactivate all
            # Reactivate all enrollments for this teacher's courses
            Enrollment.objects.filter(
                course__in=teacher_courses,
                user=restriction.student,
                is_active=False,
            ).update(is_active=True, unenrolled_at=None)

            # Restore all chat participants for this teacher's course chats
            ChatParticipant.objects.filter(
                chat_room__course__in=teacher_courses,
                chat_room__chat_type="course",
                user=restriction.student,
                is_active=False,
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

        return StudentRestriction.objects.filter(teacher=teacher)

    @staticmethod
    def get_restriction_with_permission_check(restriction_id: int, user: User):
        """Get restriction with permission check"""
        try:
            restriction = StudentRestriction.objects.get(id=restriction_id)
            
            can_view = StudentRestrictionPolicy.check_can_view_restriction(
                user, restriction, raise_exception=False
            )
            if not can_view:
                raise ServiceError.not_found("Restriction not found")
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
