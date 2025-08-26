from ..models import Course
from rest_framework import serializers
from django.utils import timezone
from .user_serializers import UserSerializer


class CourseSerializer(serializers.ModelSerializer):
    """Basic course serializer for create/update operations"""

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
        read_only_fields = [
            "id",
            "teacher",
            "created_at",
        ]
        extra_kwargs = {
            "published_at": {"required": False, "allow_null": True}
        }

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long"
            )
        return value

    def validate_description(self, value):
        if len(value) < 20:
            raise serializers.ValidationError(
                "Description must be at least 20 characters long"
            )
        return value

    def validate_published_at(self, value):
        if value:
            # Allow 10 second tolerance for network delays
            tolerance = timezone.now() - timezone.timedelta(seconds=10)
            if value < tolerance:
                raise serializers.ValidationError(
                    "Published date cannot be in the past"
                )
        return value


class CourseListSerializer(CourseSerializer):
    """Course serializer for list with basic info and teacher name"""

    teacher_name = serializers.CharField(
        source="teacher.username", read_only=True
    )

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ["teacher_name"]
        read_only_fields = CourseSerializer.Meta.read_only_fields + [
            "teacher_name"
        ]


class CourseDetailSerializer(CourseSerializer):
    """Detailed course serializer with enrollment data and nested teacher"""

    # These fields will be populated by the service layer
    enrollment_count = serializers.SerializerMethodField()
    total_enrollments = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    course_chat_id = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + [
            "updated_at",
            "enrollment_count",
            "total_enrollments",
            "is_enrolled",
            "course_chat_id",
        ]
        read_only_fields = CourseSerializer.Meta.read_only_fields + [
            "updated_at",
            "enrollment_count",
            "total_enrollments",
            "is_enrolled",
            "course_chat_id",
        ]

    def get_enrollment_count(self, obj):
        """Get enrollment count from service-populated field"""
        if hasattr(obj, '_enrollment_count'):
            return obj._enrollment_count
        return 0

    def get_total_enrollments(self, obj):
        """Get total enrollments from service-populated field"""
        if hasattr(obj, '_total_enrollments'):
            return obj._total_enrollments
        return 0

    def get_is_enrolled(self, obj):
        """Get enrollment status from service-populated field"""
        if hasattr(obj, '_is_enrolled'):
            return obj._is_enrolled
        return False

    def get_course_chat_id(self, obj):
        """Get course chat ID from service-populated field"""
        if hasattr(obj, '_course_chat_id'):
            return obj._course_chat_id
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Add nested teacher data
        data["teacher"] = UserSerializer(instance.teacher).data

        return data
