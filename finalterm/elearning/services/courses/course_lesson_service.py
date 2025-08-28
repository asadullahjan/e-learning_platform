from django.db import transaction
from elearning.models import CourseLesson, Course, File, User
from elearning.exceptions import ServiceError
from elearning.permissions.courses.lesson_permissions import LessonPolicy
from elearning.permissions.courses.file_permissions import FilePolicy
from elearning.services.courses.course_service import CourseService


class CourseLessonService:
    """Service for managing course lessons"""

    @staticmethod
    @transaction.atomic
    def create_lesson_with_file(
        course: Course, teacher: User, lesson_data: dict, file_data
    ):
        """Create a lesson with an attached file"""
        # Check if teacher can create lessons for this course
        LessonPolicy.check_can_create_lesson(
            teacher, course, raise_exception=True
        )

        # Check if teacher can upload files
        FilePolicy.check_can_upload_file(teacher, course, raise_exception=True)

        # Create the lesson
        lesson = CourseLesson.objects.create(
            course=course,
            title=lesson_data["title"],
            description=lesson_data.get("description", ""),
            content=lesson_data.get("content", ""),
        )

        # Create the file if provided
        if file_data:
            file_obj = File.objects.create(
                file=file_data,
                original_name=file_data.name,
                uploaded_by=teacher,
            )
            # Associate the file with the lesson
            lesson.file = file_obj
            lesson.save()

        return lesson

    @staticmethod
    @transaction.atomic
    def update_lesson_with_file(
        lesson: CourseLesson,
        lesson_data: dict,
        teacher: User,
        file_data=None,
    ):
        """Update a lesson and optionally its file"""
        # Check if teacher can modify this lesson
        LessonPolicy.check_can_modify_lesson(
            teacher, lesson, raise_exception=True
        )

        # Update lesson fields (exclude file field, handle separately)
        for field, value in lesson_data.items():
            if hasattr(lesson, field) and field != 'file':
                setattr(lesson, field, value)
        lesson.save()

        # Update file if provided
        if file_data:
            # Check if teacher can upload files
            FilePolicy.check_can_upload_file(
                teacher, lesson.course, raise_exception=True
            )

            # Update existing file or create new one
            if lesson.file:
                old_file = lesson.file
                # Create new file
                file_obj = File.objects.create(
                    file=file_data,
                    original_name=file_data.name,
                    uploaded_by=teacher,
                )
                lesson.file = file_obj
                lesson.save()

                # Only delete old file if not used by other lessons
                if not old_file.lessons.exclude(id=lesson.id).exists():
                    old_file.delete()
            else:
                # Create new file
                file_obj = File.objects.create(
                    file=file_data,
                    original_name=file_data.name,
                    uploaded_by=teacher,
                )
                lesson.file = file_obj
                lesson.save()

        return lesson

    @staticmethod
    @transaction.atomic
    def delete_lesson_with_file(lesson: CourseLesson, teacher: User):
        """Delete a lesson and its associated file"""
        # Check if teacher can delete this lesson
        LessonPolicy.check_can_delete_lesson(
            teacher, lesson, raise_exception=True
        )

        # Store file reference before deleting lesson
        file_to_check = lesson.file if lesson.file else None

        # Delete the lesson first
        lesson.delete()

        # Only delete associated file if it exists and is not used by other
        # lessons
        if file_to_check and not file_to_check.lessons.exists():
            file_to_check.delete()

    @staticmethod
    def toggle_lesson_publish_status(lesson: CourseLesson, published_at):
        """Set the published status of a lesson"""
        lesson.published_at = published_at
        lesson.save()
        return lesson

    @staticmethod
    def get_lesson_with_permission_check(lesson_id: int, user: User):
        """Get lesson with permission check including course access validation"""
        try:
            lesson = CourseLesson.objects.get(id=lesson_id)
            
            # First check if user can access the course this lesson belongs to
            CourseService.get_course_with_permission_check(
                lesson.course.id, user
            )
            
            # Then check if user can view this specific lesson
            LessonPolicy.check_can_view_lesson(
                user, lesson, raise_exception=True
            )
            return lesson
        except CourseLesson.DoesNotExist:
            raise ServiceError.not_found("Lesson not found")

    @staticmethod
    def get_lesson_file_with_permission_check(lesson_id: int, user: User):
        """Get lesson file with permission check"""
        try:
            lesson = CourseLesson.objects.get(id=lesson_id)
            # Check if user can view this lesson
            LessonPolicy.check_can_view_lesson(
                user, lesson, raise_exception=True
            )

            # Check if lesson has a file
            if not hasattr(lesson, "file") or not lesson.file:
                raise ServiceError.not_found("No file available for download")

            # Check if user can download the file
            FilePolicy.check_can_download_file(
                user, lesson.file, raise_exception=True
            )

            return lesson.file
        except CourseLesson.DoesNotExist:
            raise ServiceError.not_found("Lesson not found")

    @staticmethod
    def get_lessons_for_course(course: Course, user: User):
        """Get lessons for a course with permission filtering.

        Note: Course access validation (including restrictions) should be
        done by view using CourseService.get_course_with_permission_check()
        """
        # Teachers see all lessons for their courses
        if user.is_authenticated and course.teacher == user:
            return CourseLesson.objects.filter(course=course)

        # Students see only published lessons in published courses if enrolled
        if user.is_authenticated and user.role == "student":
            if (course.published_at and
                    user.enrollments.filter(
                        course=course, is_active=True
                    ).exists()):
                return CourseLesson.objects.filter(
                    course=course,
                    published_at__isnull=False,
                )

        # Unauthenticated users or non-enrolled users see nothing
        return CourseLesson.objects.none()
