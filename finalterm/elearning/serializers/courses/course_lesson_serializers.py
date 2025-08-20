import base64
from rest_framework import serializers
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

    def get_download_url(self, obj):
        request = self.context.get("request")
        lesson = self.context.get("lesson")
        if not lesson or not request:
            return None
        return request.build_absolute_uri(
            f"/api/courses/{lesson.course.id}/lessons/{lesson.id}/download/"
        )

    def get_file_content(self, obj):
        if obj.file:
            with open(obj.file.path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
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
            # Pass the lesson context to the file serializer
            file_serializer = FileSerializer(
                instance.file, context={**self.context, "lesson": instance}
            )
            data["file"] = file_serializer.data
        return data


class CourseLessonCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)

    class Meta:
        model = CourseLesson
        fields = ["title", "description", "content", "file"]


class CourseLessonUpdateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)

    class Meta:
        model = CourseLesson
        fields = ["title", "description", "content", "file", "published_at"]
