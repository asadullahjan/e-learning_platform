from rest_framework import serializers
from elearning.models import ChatMessage
from elearning.serializers.user_serializers import UserSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "content",
            "created_at",
            "updated_at",
            "sender",
            "chat_room",
        ]


class ChatMessageCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["content"]
