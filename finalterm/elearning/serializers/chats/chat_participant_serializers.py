from rest_framework import serializers
from elearning.models import ChatParticipant, User
from elearning.serializers.user_serializers import UserSerializer


class ChatParticipantListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ChatParticipant
        fields = ["user", "role", "joined_at", "is_active", "last_seen_at"]


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

    def validate(self, attrs):
        """Validate that user is not changing their own role"""
        user = attrs.get("user")
        request_user = self.context["request"].user

        if user == request_user:
            raise serializers.ValidationError("Cannot change your own role")
        return attrs


class ChatParticipantCreateSerializer(serializers.Serializer):
    """Serializer for creating chat participants"""

    username = serializers.CharField(
        required=False,
        help_text="Username to add (admin only). Leave empty to join yourself.",
    )

    def validate_username(self, value):
        """Validate username if provided"""
        if value:
            if not User.objects.filter(
                username=value, is_active=True
            ).exists():
                raise serializers.ValidationError(
                    f"User '{value}' not found or inactive"
                )
        return value
