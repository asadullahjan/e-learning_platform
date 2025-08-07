from elearning.models import Course
from rest_framework import serializers

from elearning.serializers import UserSerializer


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description"]
        read_only_fields = ["id", "teacher"]

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title too short")
        return value

    def validate_description(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("Description too short")
        return value


class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "teacher"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["teacher"] = UserSerializer(instance.teacher).data
        return data
