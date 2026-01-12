"""
Chat room serializers for managing chat conversations.

This module contains serializers for creating, updating, and displaying
chat rooms with proper participant management and room information.
"""

from rest_framework import serializers
from elearning.models import ChatRoom, User


class ChatRoomReadOnlySerializer(serializers.ModelSerializer):
    """Serializer for list and detail views."""

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "description",
            "chat_type",
            "course",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ChatRoomDetailReadOnlySerializer(serializers.ModelSerializer):
    """Serializer for detail views."""

    current_user_status = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "description",
            "chat_type",
            "course",
            "created_at",
            "updated_at",
            "current_user_status",
        ]
        read_only_fields = fields

    def get_current_user_status(self, obj):
        return getattr(obj, "_current_user_status", None)


class ChatRoomWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating chat rooms (ID-based)."""

    participants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "description",
            "chat_type",
            "course",
            "participants",
            "is_public",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Room name must be at least 3 characters long"
            )
        return value

    def validate_description(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError(
                "Description cannot exceed 500 characters"
            )
        return value

    def validate(self, attrs):
        """Custom validation for chat room creation"""
        chat_type = attrs.get("chat_type")
        course = attrs.get("course")

        # For course chats, course is required
        if chat_type == "course" and not course:
            raise serializers.ValidationError(
                {"course": "Course is required for course chat rooms."}
            )

        # For non-course chats, course should be None
        if chat_type != "course":
            attrs["course"] = None

        # direct chat requires exactly one participant
        if chat_type == "direct" and len(attrs["participants"]) != 1:
            raise serializers.ValidationError(
                {
                    "participants": (
                        "Direct chat requires exactly one participant."
                    )
                }
            )

        return attrs
