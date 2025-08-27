import base64
from django.utils import timezone
from rest_framework import serializers
from typing import Optional
from elearning.models import CourseLesson, File


class CourseLessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLesson
        fields = ["id", "title", "description", "published_at", "created_at"]


class FileSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    file_content = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            "id",
            "file_content",
            "original_name",
            "is_previewable",
            "download_url",
        ]

    def get_download_url(self, obj) -> Optional[str]:
        request = self.context.get("request")
        if not request:
            return None

        # Get lesson from the file's relationship
        if obj.lessons.exists():
            lesson = obj.lessons.first()
            course_id = lesson.course.id
            lesson_id = lesson.id
            download_path = (
                f"/api/courses/{course_id}/lessons/{lesson_id}/download/"
            )
            return request.build_absolute_uri(download_path)
        return None

    def get_file_content(self, obj) -> Optional[str]:
        if obj.file:
            try:
                # Handle file path for real files
                if hasattr(obj.file, "path"):
                    with open(obj.file.path, "rb") as f:
                        return base64.b64encode(f.read()).decode("utf-8")
                # Handle BytesIO objects (in tests)
                elif hasattr(obj.file, "read"):
                    content = obj.file.read()
                    if hasattr(obj.file, "seek"):
                        obj.file.seek(0)  # Reset file pointer
                    return base64.b64encode(content).decode("utf-8")
            except (IOError, OSError):
                return None
        return None


class CourseLessonDetailSerializer(serializers.ModelSerializer):
    file = FileSerializer(read_only=True)

    class Meta:
        model = CourseLesson
        fields = [
            "id",
            "title",
            "description",
            "content",
            "published_at",
            "file",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.file:
            # Use the file serializer with request context
            file_serializer = FileSerializer(
                instance.file, context=self.context
            )
            data["file"] = file_serializer.data
        return data


class CourseLessonCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)

    class Meta:
        model = CourseLesson
        fields = ["title", "description", "content", "file"]

    def to_representation(self, instance):
        """Use read serializer for response representation"""
        return CourseLessonDetailSerializer(
            instance, context=self.context
        ).data


class CourseLessonUpdateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)

    class Meta:
        model = CourseLesson
        fields = ["title", "description", "content", "file", "published_at"]

    def validate_published_at(self, value):
        if value:
            # Allow 10 second tolerance for network delays
            tolerance = timezone.now() - timezone.timedelta(seconds=10)
            if value < tolerance:
                raise serializers.ValidationError(
                    "Published date cannot be in the past"
                )
        return value

    def to_representation(self, instance):
        """Use read serializer for response representation"""
        return CourseLessonDetailSerializer(
            instance, context=self.context
        ).data
