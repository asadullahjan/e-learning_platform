"""
File permissions.

This module contains permission classes that control access to file
operations including upload, download, and deletion.
"""

from elearning.exceptions import ServiceError


class CourseFilePolicy:
    """
    Policy class for file operations.

    This class encapsulates all business rules for file operations
    and can be used by both permissions and services.
    """

    @staticmethod
    def check_can_upload_file(
        user, course=None, raise_exception=False
    ):
        """
        Check if user can upload a file.

        Args:
            user: User attempting to upload file
            course: Course to upload file to (optional)
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can upload file, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to upload files"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Only teachers can upload files
        if user.role != "teacher":
            error_msg = "Only teachers can upload files"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Teachers can upload files to their courses
        if course and course.teacher == user:
            return True

        # General file upload for teachers (no specific course)
        if not course:
            return True

        error_msg = "You can only upload files to your own courses"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_download_file(
        user, file_obj, raise_exception=False
    ):
        """
        Check if user can download a file.

        Args:
            user: User attempting to download file
            file_obj: File object to download
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can download file, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to download files"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # File owners can always download their files
        if file_obj.uploaded_by == user:
            return True

        # Course teachers can download files from their courses
        # Check through lesson relationship
        if file_obj.lessons.exists():
            lesson = file_obj.lessons.first()
            if lesson.course.teacher == user:
                return True

            # Students can download files from courses they're enrolled in if
            # both lesson and course are published
            if (
                user.role == "student"
                and lesson.published_at
                and lesson.course.published_at  # Course must be published
            ):
                from elearning.models import Enrollment
                if Enrollment.objects.filter(
                    user=user, course=lesson.course, is_active=True
                ).exists():
                    return True

        error_msg = "You don't have permission to download this file"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_delete_file(
        user, file_obj, raise_exception=False
    ):
        """
        Check if user can delete a file.

        Args:
            user: User attempting to delete file
            file_obj: File object to delete
            raise_exception: If True, raises ServiceError instead of
            returning False

        Returns:
            bool: True if user can delete file, False otherwise

        Raises:
            ServiceError: If raise_exception=True and validation fails
        """
        if not user.is_authenticated:
            error_msg = "You must be logged in to delete files"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # File owners can delete their files
        if file_obj.uploaded_by == user:
            return True

        # Course teachers can delete files from their courses
        # Check through lesson relationship
        if file_obj.lessons.exists():
            lesson = file_obj.lessons.first()
            if lesson.course.teacher == user:
                return True

        error_msg = "You don't have permission to delete this file"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False
