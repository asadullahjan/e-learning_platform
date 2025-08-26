from rest_framework import serializers

from elearning.models import CourseFeedback
from elearning.serializers import CourseSerializer, UserSerializer


class CourseFeedbackCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeedback
        fields = ["rating", "text"]

    def validate(self, data):
        # ✅ CORRECT: Only validation logic, no database queries
        rating = data.get("rating")
        text = data.get("text")
        
        if rating and (rating < 1 or rating > 5):
            raise serializers.ValidationError(
                "Rating must be between 1 and 5"
            )
        
        if text and len(text.strip()) < 10:
            raise serializers.ValidationError(
                "Feedback text must be at least 10 characters long"
            )
        
        return data


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
