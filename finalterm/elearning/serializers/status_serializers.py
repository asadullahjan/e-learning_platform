from rest_framework import serializers
from elearning.models import Status
from .user_serializers import UserSerializer


class StatusListSerializer(serializers.ModelSerializer):
    """Status serializer for list views - returns full user object"""

    user = UserSerializer()

    class Meta:
        model = Status
        fields = ["id", "user", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class StatusSerializer(serializers.ModelSerializer):
    """Detailed status serializer for retrieve operations"""

    user = UserSerializer()

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

    def to_representation(self, instance):
        """Use read serializer for response representation"""
        return StatusSerializer(instance, context=self.context).data
