from django.core.files.storage import FileSystemStorage


class PrivateCourseStorage(FileSystemStorage):
    def __init__(self):
        from django.conf import settings

        super().__init__(location=settings.PRIVATE_MEDIA_ROOT, base_url=None)
