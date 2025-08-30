"""
Course lesson serializers for managing course content.

This module contains serializers for creating, updating, and displaying
course lessons with proper validation and file handling.
"""

from typing import Optional
from rest_framework import serializers
from elearning.models import CourseLesson, File
import base64
from django.utils import timezone


class FileSerializer(serializers.ModelSerializer):
    """
    Serializer for handling file metadata and inline content.
    """

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
        read_only_fields = fields

    def get_download_url(self, obj) -> Optional[str]:
        request = self.context.get("request")
        if not request:
            return None

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
                if hasattr(obj.file, "path"):
                    with open(obj.file.path, "rb") as f:
                        return base64.b64encode(f.read()).decode("utf-8")
                elif hasattr(obj.file, "read"):
                    content = obj.file.read()
                    if hasattr(obj.file, "seek"):
                        obj.file.seek(0)
                    return base64.b64encode(content).decode("utf-8")
            except (IOError, OSError):
                return None
        return None


class CourseLessonReadOnlySerializer(serializers.ModelSerializer):
    """
    Read only serializer for detail view
    """

    file = FileSerializer(read_only=True)

    class Meta:
        model = CourseLesson
        fields = [
            "id",
            "title",
            "content",
            "course",
            "file",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.file:
            # Use the file serializer with request context
            file_serializer = FileSerializer(
                instance.file, context=self.context
            )
            data["file"] = file_serializer.data
        return data


class CourseLessonListReadOnlySerializer(CourseLessonReadOnlySerializer):
    """
    Read-only serializer for list view
    """

    class Meta(CourseLessonReadOnlySerializer.Meta):
        fields = [
            "id",
            "title",
            "course",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = fields


class CourseLessonWriteSerializer(serializers.ModelSerializer):
    """
    Single serializer for creating and updating lessons.
    """

    file = serializers.FileField(required=False)

    class Meta:
        model = CourseLesson
        fields = ["title", "description", "content", "file", "published_at"]

    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long"
            )
        return value

    def validate_content(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                "Content must be at least 10 characters long"
            )
        return value

    def validate_published_at(self, value):
        if value:
            tolerance = timezone.now() - timezone.timedelta(seconds=10)
            if value < tolerance:
                raise serializers.ValidationError(
                    "Published date cannot be in the past"
                )
        return value
