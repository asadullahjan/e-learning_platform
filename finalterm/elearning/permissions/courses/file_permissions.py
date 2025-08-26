from elearning.exceptions import ServiceError


class FilePolicy:
    """Policy class for file operations"""

    @staticmethod
    def check_can_upload_file(user, course=None, raise_exception=False):
        """Check if user can upload a file"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to upload files"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # Teachers can upload files to their courses
        if user.role == "teacher":
            if course and course.teacher == user:
                return True
            if not course:  # General file upload
                return True

        # Students can upload files to courses they're enrolled in
        if user.role == "student" and course:
            from elearning.models import Enrollment
            if Enrollment.objects.filter(
                user=user, course=course, is_active=True
            ).exists():
                return True

        error_msg = "You don't have permission to upload files"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_download_file(user, file_obj, raise_exception=False):
        """Check if user can download a file"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to download files"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # File owners can always download their files
        if file_obj.uploaded_by == user:
            return True

        # Course teachers can download files from their courses
        if hasattr(file_obj, 'course') and file_obj.course:
            if file_obj.course.teacher == user:
                return True

            # Students can download files from courses they're enrolled in
            if user.role == "student":
                from elearning.models import Enrollment
                if Enrollment.objects.filter(
                    user=user, course=file_obj.course, is_active=True
                ).exists():
                    return True

        error_msg = "You don't have permission to download this file"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False

    @staticmethod
    def check_can_delete_file(user, file_obj, raise_exception=False):
        """Check if user can delete a file"""
        if not user.is_authenticated:
            error_msg = "You must be logged in to delete files"
            if raise_exception:
                raise ServiceError.permission_denied(error_msg)
            return False

        # File owners can delete their files
        if file_obj.uploaded_by == user:
            return True

        # Course teachers can delete files from their courses
        if hasattr(file_obj, 'course') and file_obj.course:
            if file_obj.course.teacher == user:
                return True

        error_msg = "You don't have permission to delete this file"
        if raise_exception:
            raise ServiceError.permission_denied(error_msg)
        return False
