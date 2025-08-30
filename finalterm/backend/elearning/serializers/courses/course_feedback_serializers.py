"""
Course feedback serializers for managing student feedback.

This module contains serializers for creating, updating, and displaying
course feedback with proper validation and user information.
"""

from rest_framework import serializers
from elearning.models import CourseFeedback
from elearning.serializers.user_serializers import UserReadOnlySerializer
from elearning.serializers.courses.course_serializers import (
    CourseReadOnlySerializer,
)


class CourseFeedbackReadOnlySerializer(serializers.ModelSerializer):
    """
    Base read-only serializer for course feedback.
    """

    class Meta:
        model = CourseFeedback
        fields = ["id", "user", "course", "rating", "text", "created_at"]
        read_only_fields = fields


class CourseFeedbackReadOnlyForTeacherSerializer(
    CourseFeedbackReadOnlySerializer
):
    """
    Read-only serializer for course feedback lists.
    Expands user details (who gave the feedback).
    """

    user = UserReadOnlySerializer()

    class Meta(CourseFeedbackReadOnlySerializer.Meta):
        fields = CourseFeedbackReadOnlySerializer.Meta.fields


class CourseFeedbackReadOnlyForUserSerializer(
    CourseFeedbackReadOnlySerializer
):
    """
    Read-only serializer for user feedback lists.
    Expands course details (which course the feedback belongs to).
    """

    course = CourseReadOnlySerializer()

    class Meta(CourseFeedbackReadOnlySerializer.Meta):
        fields = CourseFeedbackReadOnlySerializer.Meta.fields


class CourseFeedbackWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating course feedback.
    Includes validation for rating and text content.
    """

    class Meta:
        model = CourseFeedback
        fields = ["id", "rating", "text"]
        read_only_fields = ["id"]

    def validate_rating(self, value):
        """Validate rating is within valid range"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_text(self, value):
        """Validate text content length"""
        if value and len(value) > 1000:
            raise serializers.ValidationError(
                "Text cannot exceed 1000 characters"
            )
        return value
