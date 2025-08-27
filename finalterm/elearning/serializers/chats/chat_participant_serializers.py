from rest_framework import serializers
from elearning.models import ChatParticipant, User
from elearning.serializers.user_serializers import UserSerializer


class ChatParticipantListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ChatParticipant
        fields = [
            "id",
            "user",
            "role",
            "joined_at",
            "is_active",
            "last_seen_at",
        ]


class ChatParticipantRoleUpdateSerializer(serializers.ModelSerializer):
    """Only for admins to change roles - requires user and role fields"""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), help_text="User ID to update role for"
    )

    class Meta:
        model = ChatParticipant
        fields = ["user", "role"]

    def validate_role(self, value):
        """Validate role changes"""
        if value not in ["admin", "participant"]:
            raise serializers.ValidationError("Invalid role")
        return value

    def validate_user(self, value):
        """Validate that user field is provided"""
        if not value:
            raise serializers.ValidationError("User field is required")
        return value


class ChatParticipantCreateSerializer(serializers.Serializer):
    """Serializer for creating chat participants"""

    username = serializers.CharField(
        required=False,
        help_text=(
            "Username to add (admin only). Leave empty to join yourself."
        ),
    )

    def validate_username(self, value):
        """Validate username format only"""
        if value:
            # ✅ CORRECT: Only format validation, no database queries
            if len(value.strip()) < 3:
                raise serializers.ValidationError(
                    "Username must be at least 3 characters long"
                )

            if not value.replace("_", "").replace("-", "").isalnum():
                raise serializers.ValidationError(
                    "Username can only contain letters, numbers, "
                    "underscores, and hyphens"
                )
        return value
