from rest_framework import serializers

from elearning.models import CourseFeedback
from elearning.serializers import CourseSerializer, UserSerializer


class CourseFeedbackCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFeedback
        fields = ["rating", "text"]

    def validate(self, data):
        request = self.context.get("request")
        course_id = self.context.get("course_id")

        if request and course_id and not self.instance:
            # Check if user already left feedback for this course
            # (only when creating)
            existing = CourseFeedback.objects.filter(
                user=request.user, course_id=course_id
            ).first()

            if existing:
                raise serializers.ValidationError(
                    "You have already left feedback for this course"
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
