from rest_framework import serializers
from elearning.models import ChatParticipant, User
from elearning.serializers.user_serializers import UserReadOnlySerializer


class ChatParticipantReadOnlySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for chat participants.
    Expands user details for display.
    """

    user = UserReadOnlySerializer()

    class Meta:
        model = ChatParticipant
        fields = ["id", "user", "role", "is_active", "joined_at"]
        read_only_fields = fields


class ChatParticipantWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer for adding/updating chat participants.

    - `user` is provided in payload as User instance
    - If no user provided, uses current request.user
    - `joined_at` is system-managed
    - Used for: create, update_role, deactivate, reactivate
    """

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = ChatParticipant
        fields = ["id", "user", "role"]
        read_only_fields = ["id"]

    def validate_role(self, value):
        if value not in dict(ChatParticipant.ROLE_CHOICES):
            raise serializers.ValidationError("Invalid role")
        return value
