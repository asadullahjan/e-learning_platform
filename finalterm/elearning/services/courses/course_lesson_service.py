from django.db import transaction
from elearning.models import CourseLesson, Course, File, User
from elearning.exceptions import ServiceError
from elearning.permissions.courses.lesson_permissions import LessonPolicy
from elearning.permissions.courses.file_permissions import FilePolicy


class CourseLessonService:
    """Service for managing course lessons"""

    @staticmethod
    @transaction.atomic
    def create_lesson_with_file(
        course: Course, teacher: User, lesson_data: dict, file_data: dict
    ):
        """Create a lesson with an attached file"""
        # Check if teacher can create lessons for this course
        LessonPolicy.check_can_create_lesson(
            teacher, course, raise_exception=True
        )

        # Check if teacher can upload files
        FilePolicy.check_can_upload_file(
            teacher, course, raise_exception=True
        )

        # Create the lesson
        lesson = CourseLesson.objects.create(
            course=course,
            title=lesson_data["title"],
            content=lesson_data.get("content", ""),
            order=lesson_data.get("order", 0),
            created_by=teacher,
        )

        # Create the file
        file_obj = File.objects.create(
            file=file_data["file"],
            filename=file_data.get("filename", file_data["file"].name),
            file_type=file_data.get("file_type", "lesson_material"),
            uploaded_by=teacher,
            course=course,
            lesson=lesson,
        )

        return lesson, file_obj

    @staticmethod
    @transaction.atomic
    def update_lesson_with_file(
        lesson: CourseLesson, teacher: User, lesson_data: dict, file_data: dict = None
    ):
        """Update a lesson and optionally its file"""
        # Check if teacher can modify this lesson
        LessonPolicy.check_can_modify_lesson(
            teacher, lesson, raise_exception=True
        )

        # Update lesson fields
        for field, value in lesson_data.items():
            if hasattr(lesson, field):
                setattr(lesson, field, value)
        lesson.save()

        # Update file if provided
        if file_data:
            # Check if teacher can upload files
            FilePolicy.check_can_upload_file(
                teacher, lesson.course, raise_exception=True
            )

            # Update existing file or create new one
            if hasattr(lesson, 'file') and lesson.file:
                # Update existing file
                file_obj = lesson.file
                file_obj.file = file_data["file"]
                file_obj.filename = file_data.get("filename", file_data["file"].name)
                file_obj.file_type = file_data.get("file_type", "lesson_material")
                file_obj.save()
            else:
                # Create new file
                file_obj = File.objects.create(
                    file=file_data["file"],
                    filename=file_data.get("filename", file_data["file"].name),
                    file_type=file_data.get("file_type", "lesson_material"),
                    uploaded_by=teacher,
                    course=lesson.course,
                    lesson=lesson,
                )

        return lesson

    @staticmethod
    @transaction.atomic
    def delete_lesson_with_file(lesson: CourseLesson, teacher: User):
        """Delete a lesson and its associated file"""
        # Check if teacher can delete this lesson
        LessonPolicy.check_can_delete_lesson(
            teacher, lesson, raise_exception=True
        )

        # Delete associated file if it exists
        if hasattr(lesson, 'file') and lesson.file:
            lesson.file.delete()

        # Delete the lesson
        lesson.delete()

    @staticmethod
    def toggle_lesson_publish_status(lesson: CourseLesson, teacher: User):
        """Toggle the published status of a lesson"""
        # Check if teacher can modify this lesson
        LessonPolicy.check_can_modify_lesson(
            teacher, lesson, raise_exception=True
        )

        lesson.published_at = (
            None if lesson.published_at else lesson.created_at
        )
        lesson.save()
        return lesson

    @staticmethod
    def get_lesson_with_permission_check(lesson_id: int, user: User):
        """Get lesson with permission check"""
        try:
            lesson = CourseLesson.objects.get(id=lesson_id)
            # Check if user can view this lesson
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
            if not hasattr(lesson, 'file') or not lesson.file:
                raise ServiceError.not_found("Lesson has no attached file")
            
            # Check if user can download the file
            FilePolicy.check_can_download_file(
                user, lesson.file, raise_exception=True
            )
            
            return lesson.file
        except CourseLesson.DoesNotExist:
            raise ServiceError.not_found("Lesson not found")
