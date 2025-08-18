from rest_framework import serializers
from ...models import ChatRoom, User, ChatParticipant


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

    # Add current user's participant status
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
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return {"is_participant": False, "role": None}

        try:
            participant = ChatParticipant.objects.get(
                chat_room=obj, user=request.user, is_active=True
            )
            return {"is_participant": True, "role": participant.role}
        except ChatParticipant.DoesNotExist:
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
        """Validate participant IDs exist and remove duplicates"""
        if not value:
            return []

        # Remove duplicates while preserving order
        unique_ids = list(dict.fromkeys(value))

        # Check if all users exist
        existing_users_count = User.objects.filter(id__in=unique_ids).count()
        if existing_users_count != len(unique_ids):
            raise serializers.ValidationError(
                "Some participant users do not exist"
            )

        return unique_ids

    def to_internal_value(self, data):
        """Transform participant IDs to User instances"""
        validated_data = super().to_internal_value(data)

        # Transform participant IDs to User instances
        participant_ids = validated_data.get("participants", [])
        if participant_ids:
            participants = list(User.objects.filter(id__in=participant_ids))
            creator = self.context["request"].user

            # Remove creator from participants if they included themselves
            if creator in participants:
                participants.remove(creator)

            validated_data["participants"] = participants
        else:
            validated_data["participants"] = []

        return validated_data

    def validate(self, attrs):
        """Cross-field validation only"""
        chat_type = attrs.get("chat_type")
        course = attrs.get("course")
        participants = attrs.get("participants", [])

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
            if len(participants) != 1:
                raise serializers.ValidationError(
                    "Direct chats must have exactly 1 participant specified "
                    "(creator will be added automatically)"
                )

        return attrs
