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
