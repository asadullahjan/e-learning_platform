"""
Course student restriction serializers for managing student access.

This module contains serializers for creating, updating, and displaying
student restrictions with proper validation and course information.
"""

from rest_framework import serializers
from elearning.models import StudentRestriction
from elearning.serializers.user_serializers import UserReadOnlySerializer
from elearning.serializers.courses.course_serializers import (
    CourseReadOnlySerializer,
)


class CourseStudentRestrictionReadOnlySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for student restrictions.
    Used for both list and detail views.
    """

    user = UserReadOnlySerializer()
    course = CourseReadOnlySerializer()

    class Meta:
        model = StudentRestriction
        fields = [
            "id",
            "user",
            "course",
            "reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CourseStudentRestrictionWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating student restrictions.

    - Expects student and course in payload for creation.
    """

    class Meta:
        model = StudentRestriction
        fields = ["id", "student", "course", "reason"]
        read_only_fields = ["id"]

    def validate_reason(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Reason cannot be empty")
        if len(value) > 500:
            raise serializers.ValidationError(
                "Reason cannot exceed 500 characters"
            )
        return value
