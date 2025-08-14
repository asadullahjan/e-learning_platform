from rest_framework import serializers
from elearning.models import ChatParticipant
from elearning.serializers.user_serializers import UserSerializer


class ChatParticipantListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ChatParticipant
        fields = ["user", "role", "joined_at", "is_active", "last_seen_at"]


class ChatParticipantCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatParticipant
        fields = ["user", "role"]
