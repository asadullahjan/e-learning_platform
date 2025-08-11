from rest_framework import serializers
from ...models import ChatRoom


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
    class Meta:
        model = ChatRoom
        fields = "__all__"

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Name must be at least 3 characters long"
            )
        return value

    def validate(self, attrs):
        chat_type = attrs.get("chat_type")
        course = attrs.get("course")

        if chat_type == "course" and not course:
            raise serializers.ValidationError(
                "Course is required for course-wide chat"
            )

        if chat_type != "course" and course:
            raise serializers.ValidationError(
                "Course is not allowed for non-course-wide chat"
            )

        return attrs
