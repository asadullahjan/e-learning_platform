from rest_framework import serializers
from elearning.models import Status, User
from .user_serializers import UserSerializer


class StatusSerializer(serializers.ModelSerializer):
    """Basic status serializer for all operations"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Status
        fields = ["id", "user", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class StatusCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating status updates"""

    class Meta:
        model = Status
        fields = ["content"]

    def validate_content(self, value):
        """Validate status content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Status content cannot be empty")
        if len(value) > 500:
            raise serializers.ValidationError(
                "Status content cannot exceed 500 characters"
            )
        return value.strip()

    def create(self, validated_data):
        """Set the user from the request"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class UserStatusesQuerySerializer(serializers.Serializer):
    """Serializer for validating user_statuses query parameters"""

    user_id = serializers.IntegerField(
        required=True,
        error_messages={
            "required": "user_id parameter is required",
            "invalid": "user_id must be a valid integer",
        },
    )

    def validate_user_id(self, value):
        """Validate that user_id exists"""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value
