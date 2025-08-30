"""
Chat message serializers for managing chat communications.

This module contains serializers for creating, updating, and displaying
chat messages with proper user information and content handling.
"""

from rest_framework import serializers
from elearning.models import ChatMessage
from elearning.serializers.user_serializers import UserReadOnlySerializer


class ChatMessageReadOnlySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for chat messages.
    Expands sender details for display purposes.
    """

    sender = UserReadOnlySerializer()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "content",
            "created_at",
            "updated_at",
            "sender",
            "chat_room",
        ]
        read_only_fields = fields


class ChatMessageWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer for creating/updating chat messages.

    - `sender` comes from request.user
    - `chat_room` comes from URL / view context
    """

    class Meta:
        model = ChatMessage
        fields = ["id", "content"]
        read_only_fields = ["id"]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Message too long")
        return value.strip()
