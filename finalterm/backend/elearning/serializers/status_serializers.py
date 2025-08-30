"""
Status serializers for user status updates and activity tracking.

This module contains serializers for creating, updating, and displaying
user status updates with proper validation and representation.
"""

from rest_framework import serializers
from elearning.models import Status
from .user_serializers import UserReadOnlySerializer


class StatusReadOnlySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for status updates.
    Includes nested user details using UserReadonlySerializer.
    """

    user = UserReadOnlySerializer()

    class Meta:
        model = Status
        fields = ["id", "user", "content", "created_at", "updated_at"]
        read_only_fields = fields


class StatusWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating status updates.
    Only `content` is writable. `user` is injected from request.user.
    """

    class Meta:
        model = Status
        fields = ["id", "content"]
        read_only_fields = ["id"]

    def validate_content(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Status content cannot be empty")
        if len(value) > 500:
            raise serializers.ValidationError(
                "Status content cannot exceed 500 characters"
            )
        return value
