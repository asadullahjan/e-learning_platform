from rest_framework import serializers

from elearning.models import CourseFeedback
from elearning.serializers.user_serializers import UserSerializer
from elearning.serializers.courses.course_serializers import CourseSerializer


class CourseFeedbackCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeedback
        fields = ["rating", "text"]

    def validate(self, data):
        # ✅ CORRECT: Only validation logic, no database queries
        rating = data.get("rating")
        text = data.get("text")

        if rating is not None and (rating < 1 or rating > 5):
            raise serializers.ValidationError(
                {"rating": "Rating must be between 1 and 5"}
            )

        if text is not None and len(text.strip()) < 10:
            raise serializers.ValidationError(
                {"text": "Feedback text must be at least 10 characters long"}
            )

        if text is not None and len(text.strip()) > 500:
            raise serializers.ValidationError(
                {"text": "Feedback text cannot exceed 500 characters"}
            )

        return data

    def to_representation(self, instance):
        """Use read serializer for response representation"""
        return CourseFeedbackListSerializerForCourse(
            instance, context=self.context
        ).data


class CourseFeedbackListSerializerForUser(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = CourseFeedback
        fields = ["id", "rating", "text", "created_at", "course"]
        read_only_fields = ["id", "created_at", "course"]


class CourseFeedbackListSerializerForCourse(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CourseFeedback
        fields = ["id", "rating", "text", "created_at", "user"]
        read_only_fields = ["id", "created_at", "user"]
