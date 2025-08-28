from django.db import transaction
from elearning.models import Course, ChatRoom, ChatParticipant, User
from elearning.exceptions import ServiceError
from elearning.permissions.courses.course_permissions import CoursePolicy
from elearning.services.courses.student_restriction_service import (
    StudentRestrictionService,
)


class CourseService:
    """
    Service for managing course operations and business logic.

    This service encapsulates all business logic related to courses including:
    - Course creation and management
    - Course access control and permissions
    - Course listing and filtering based on user roles

    The service follows the single responsibility principle and provides
    a clean interface for views to interact with course-related operations.
    """

    @staticmethod
    @transaction.atomic
    def create_course_with_chat(teacher, course_data):
        """
        Create a course and its associated chat room.

        This method creates a course and automatically sets up the associated
        chat room for student-teacher communication. The operation is wrapped
        in a database transaction to ensure data consistency.

        Args:
            teacher: User object (must be a teacher)
            course_data: Validated course data from serializer

        Returns:
            Course instance with chat room created

        Raises:
            ServiceError: If teacher validation fails

        Example:
            >>> course_data = {'title': 'Python Basics', 'description': '...'}
            >>> course = CourseService.create_course_with_chat(
            ...     teacher, course_data
            ... )
            >>> print(f"Created course: {course.title}")
        """
        # Use the permission policy for validation
        CoursePolicy.check_can_create_course(teacher, raise_exception=True)

        # Create the course
        course = Course.objects.create(teacher=teacher, **course_data)

        # Create the chatroom for the course
        chatroom = ChatRoom.objects.create(
            name=f"{course.title} Chat",
            course=course,
            chat_type="course",
            is_public=True,
            created_by=teacher,
        )

        # Add the course creator as admin participant
        ChatParticipant.objects.create(
            chat_room=chatroom, user=teacher, role="admin"
        )

        return course

    @staticmethod
    def get_courses_for_user(user):
        """
        Get courses based on user role and permissions.

        This method implements the business logic for course visibility:
        - Anonymous users see only published courses
        - Teachers see published courses plus their own courses
        - Students see only published courses

        Args:
            user: User object requesting courses

        Returns:
            QuerySet of courses filtered by user permissions

        Example:
            >>> courses = CourseService.get_courses_for_user(user)
            >>> for course in courses:
            ...     print(f"Available course: {course.title}")
        """
        if not user.is_authenticated:
            # Return only published courses for anonymous users
            return Course.objects.filter(published_at__isnull=False)

        if user.role == "teacher":
            # Teachers see published courses + their own courses
            published_courses = Course.objects.filter(
                published_at__isnull=False
            )
            user_courses = Course.objects.filter(teacher=user)
            return (published_courses | user_courses).distinct()

        # Students see only published courses they're not restricted from
        published_courses = Course.objects.filter(published_at__isnull=False)

        # Filter courses using optimized restriction checking
        if user.role == "student":
            # Get all restricted course IDs using optimized method
            restricted_course_ids = (
                StudentRestrictionService.get_restricted_courses_for_student(
                    user
                )
            )
            if restricted_course_ids:
                return published_courses.exclude(id__in=restricted_course_ids)
            else:
                return published_courses

        return published_courses

    @staticmethod
    def update_course(course: Course, course_data: dict, user: User):
        """Update course with permission check"""
        # Check if user can modify this course
        CoursePolicy.check_can_modify_course(
            user, course, raise_exception=True
        )

        # Update course fields
        for field, value in course_data.items():
            if hasattr(course, field):
                setattr(course, field, value)

        course.save()
        return course

    @staticmethod
    def delete_course(course: Course, user: User):
        """Delete course with permission check"""
        # Check if user can delete this course
        CoursePolicy.check_can_delete_course(
            user, course, raise_exception=True
        )

        # Delete the course (this will cascade to related objects)
        course.delete()

    @staticmethod
    def get_course_with_permission_check(course_id: int, user: User):
        """Get course with permission check including restrictions."""
        try:
            course = Course.objects.get(id=course_id)
            # Check if user can access this course (includes restrictions)
            CoursePolicy.check_can_access_course(
                user, course, raise_exception=True
            )
            return course
        except Course.DoesNotExist:
            raise ServiceError.not_found("Course not found")

    @staticmethod
    def populate_course_computed_fields(course: Course, user: User = None):
        """Populate computed fields for course serialization"""
        # Get enrollment counts
        course._enrollment_count = course.enrollments.filter(
            is_active=True
        ).count()
        course._total_enrollments = course.enrollments.count()

        # Check if user is enrolled
        if user and user.is_authenticated:
            course._is_enrolled = course.enrollments.filter(
                user=user, is_active=True
            ).exists()
        else:
            course._is_enrolled = False

        # Get course chat ID
        try:
            course_chat = ChatRoom.objects.get(
                chat_type="course", course=course
            )
            course._course_chat_id = course_chat.id
        except ChatRoom.DoesNotExist:
            course._course_chat_id = None

        return course

    @staticmethod
    def get_courses_with_computed_fields(user: User = None):
        """Get courses with computed fields populated"""
        courses = CourseService.get_courses_for_user(user)

        # Populate computed fields for each course
        for course in courses:
            CourseService.populate_course_computed_fields(course, user)

        return courses
