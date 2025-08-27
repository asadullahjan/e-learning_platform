from rest_framework import serializers
from typing import Dict, Any
from elearning.models import ChatRoom


class ChatRoomListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "created_at",
            "description",
            "chat_type",
            "course",
            "is_public",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by", "course"]


class ChatRoomSerializer(serializers.ModelSerializer):
    """Read serializer for chat room details"""

    # This field will be populated by the service layer
    current_user_status = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "description",
            "chat_type",
            "created_by",
            "course",
            "is_public",
            "created_at",
            "updated_at",
            "current_user_status",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "current_user_status",
        ]

    def get_current_user_status(self, obj) -> Dict[str, Any]:
        """Get current user's participant status for this chat room"""
        # This will be populated by the service layer before serialization
        if hasattr(obj, "_current_user_status"):
            return obj._current_user_status
        return {"is_participant": False, "role": None}


class ChatRoomCreateUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for creating and updating chat rooms"""

    participants = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of user IDs to add as participants",
    )

    class Meta:
        model = ChatRoom
        fields = [
            "name",
            "description",
            "chat_type",
            "course",
            "is_public",
            "participants",
        ]

    def validate_name(self, value):
        """Validate chat room name"""
        if len(value) < 3:
            raise serializers.ValidationError(
                "Name must be at least 3 characters long"
            )
        return value

    def validate_chat_type(self, value):
        """Validate chat type is allowed"""
        if value not in [
            chat_type[0] for chat_type in ChatRoom.CHAT_TYPE_CHOICES
        ]:
            raise serializers.ValidationError("Invalid chat type")
        return value

    def validate_participants(self, value):
        """Validate participant IDs format only"""
        if not value:
            return []

        # Only format validation, no database queries
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Participants must be a list of user IDs"
            )

        # Check if all IDs are positive integers
        for user_id in value:
            if not isinstance(user_id, int) or user_id <= 0:
                raise serializers.ValidationError(
                    "All participant IDs must be positive integers"
                )

        # Remove duplicates while preserving order
        return list(dict.fromkeys(value))

    def validate(self, attrs):
        """Cross-field validation"""
        chat_type = attrs.get("chat_type")
        course = attrs.get("course")
        participants = attrs.get("participants", [])

        # Business logic validation
        if chat_type == "course" and not course:
            raise serializers.ValidationError(
                {"course": ["Course is required for course-wide chat"]}
            )

        if chat_type != "course" and course:
            raise serializers.ValidationError(
                {"course": ["Course is not allowed for non-course-wide chat"]}
            )

        if chat_type == "direct":
            if len(participants) != 1:
                raise serializers.ValidationError(
                    {"participants": [
                        "Direct chats must have exactly 1 participant "
                        "specified (creator will be added automatically)"
                    ]}
                )

        return attrs

    def to_representation(self, instance):
        """Use read serializer for response representation"""
        return ChatRoomSerializer(instance, context=self.context).data
