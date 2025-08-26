from rest_framework import serializers
from elearning.models import ChatRoom


class ChatRoomListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "created_at",
            "chat_type",
            "course",
            "is_public",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "created_by", "course"]


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    # This field will be populated by the service layer
    current_user_status = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "name",
            "chat_type",
            "created_by",
            "course",
            "is_public",
            "created_at",
            "updated_at",
            "participants",
            "current_user_status",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "current_user_status",
        ]

    def get_current_user_status(self, obj):
        """Get current user's participant status for this chat room"""
        # This will be populated by the service layer before serialization
        if hasattr(obj, '_current_user_status'):
            return obj._current_user_status
        return {"is_participant": False, "role": None}

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Name must be at least 3 characters long"
            )
        return value

    def validate_chat_type(self, value):
        if value not in [
            chat_type[0] for chat_type in ChatRoom.CHAT_TYPE_CHOICES
        ]:
            raise serializers.ValidationError("Invalid chat type")
        return value

    def validate_participants(self, value):
        """Validate participant IDs format only"""
        if not value:
            return []

        # ✅ CORRECT: Only format validation, no database queries
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

    def to_internal_value(self, data):
        """Transform participant IDs to User instances"""
        validated_data = super().to_internal_value(data)

        # ✅ CORRECT: Transform data, but don't validate existence here
        participant_ids = validated_data.get("participants", [])
        if participant_ids:
            # Store IDs for later validation in service
            validated_data["participant_ids"] = participant_ids
            validated_data["participants"] = []
        else:
            validated_data["participants"] = []

        return validated_data

    def validate(self, attrs):
        """Cross-field validation only"""
        chat_type = attrs.get("chat_type")
        course = attrs.get("course")
        participant_ids = attrs.get("participant_ids", [])

        # Business logic validation
        if chat_type == "course" and not course:
            raise serializers.ValidationError(
                "Course is required for course-wide chat"
            )

        if chat_type != "course" and course:
            raise serializers.ValidationError(
                "Course is not allowed for non-course-wide chat"
            )

        if chat_type == "direct":
            if len(participant_ids) != 1:
                raise serializers.ValidationError(
                    "Direct chats must have exactly 1 participant specified "
                    "(creator will be added automatically)"
                )

        return attrs
