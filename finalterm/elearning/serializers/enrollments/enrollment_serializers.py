from elearning.models import Enrollment
from rest_framework import serializers
from elearning.serializers import CourseSerializer, UserSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    """Basic enrollment serializer"""

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "user",
            "enrolled_at",
            "is_active",
            "unenrolled_at",
        ]
        read_only_fields = ["id", "user", "enrolled_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        course = attrs.get("course")

        # Check if already enrolled
        if Enrollment.objects.filter(
            user=user, course=course, is_active=True
        ).exists():
            raise serializers.ValidationError(
                "You are already enrolled in this course"
            )

        # Check if course is published
        if not course.published_at:
            raise serializers.ValidationError(
                "Cannot enroll in unpublished course"
            )

        return attrs


class EnrollmentDetailSerializer(EnrollmentSerializer):
    """Detailed enrollment serializer with nested data"""

    course = CourseSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta(EnrollmentSerializer.Meta):
        fields = EnrollmentSerializer.Meta.fields + [
            "course_details",
            "user_details",
        ]
        read_only_fields = EnrollmentSerializer.Meta.read_only_fields + [
            "course",
            "user",
        ]
