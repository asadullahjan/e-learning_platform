from rest_framework import serializers
from elearning.models import Course
from elearning.serializers.user_serializers import UserReadOnlySerializer
from django.utils import timezone
from typing import Optional


class CourseValidationConstants:
    """Constants for course validation rules."""

    MIN_TITLE_LENGTH = 5
    MIN_DESCRIPTION_LENGTH = 20
    PUBLISH_TOLERANCE_SECONDS = 10


class CourseWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating courses.
    Accepts title, description, and published_at.
    Teacher and created_at are handled automatically.
    """

    class Meta:
        model = Course
        fields = ["id", "title", "description", "published_at"]
        read_only_fields = ["id"]

    def validate_title(self, value: str) -> str:
        if len(value.strip()) < CourseValidationConstants.MIN_TITLE_LENGTH:
            raise serializers.ValidationError(
                "Title must be at least"
                f"{CourseValidationConstants.MIN_TITLE_LENGTH} characters long"
            )
        return value.strip()

    def validate_description(self, value: str) -> str:
        if (
            len(value.strip())
            < CourseValidationConstants.MIN_DESCRIPTION_LENGTH
        ):
            raise serializers.ValidationError(
                "Description must be at least"
                f"{CourseValidationConstants.MIN_DESCRIPTION_LENGTH}"
                "characters long"
            )
        return value.strip()

    def validate_published_at(
        self, value: Optional[timezone.datetime]
    ) -> Optional[timezone.datetime]:
        if value:
            tolerance = timezone.now() - timezone.timedelta(
                seconds=CourseValidationConstants.PUBLISH_TOLERANCE_SECONDS
            )
            if value < tolerance:
                raise serializers.ValidationError(
                    "Published date cannot be in the past"
                )
        return value


class CourseReadOnlySerializer(serializers.ModelSerializer):
    """
    Full read-only serializer for detailed course views.
    Includes teacher info, enrollment stats, and chat ID.
    """

    teacher = UserReadOnlySerializer()
    enrollment_count = serializers.SerializerMethodField()
    total_enrollments = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    course_chat_id = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "teacher",
            "created_at",
            "updated_at",
            "published_at",
            "enrollment_count",
            "total_enrollments",
            "is_enrolled",
            "course_chat_id",
        ]
        read_only_fields = fields

    def get_enrollment_count(self, obj: Course) -> int:
        return getattr(obj, "_enrollment_count", 0)

    def get_total_enrollments(self, obj: Course) -> int:
        return getattr(obj, "_total_enrollments", 0)

    def get_is_enrolled(self, obj: Course) -> bool:
        return getattr(obj, "_is_enrolled", False)

    def get_course_chat_id(self, obj: Course) -> Optional[int]:
        return getattr(obj, "_course_chat_id", None)


class CourseListReadOnlySerializer(serializers.ModelSerializer):
    """
    Simplified read-only serializer for course lists.
    Includes nested teacher info.
    """

    teacher = UserReadOnlySerializer()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "teacher",
            "published_at",
            "created_at",
        ]
        read_only_fields = fields
