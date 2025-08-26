from ..models import Enrollment
from rest_framework import serializers
from .user_serializers import UserSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    """Basic enrollment serializer for general use"""

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
        read_only_fields = ["id", "user", "enrolled_at", "course"]


class StudentEnrollmentCourseSerializer(serializers.ModelSerializer):
    """Course serializer for student enrollments with full teacher details"""
    
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Enrollment.course.field.related_model
        fields = [
            "id",
            "title",
            "description",
            "teacher",
            "published_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "title",
            "description",
            "teacher",
            "published_at",
            "created_at",
        ]


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    """Enrollment serializer for students - shows course details with full teacher info"""

    course = StudentEnrollmentCourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "enrolled_at",
            "is_active",
            "unenrolled_at",
        ]
        read_only_fields = ["id", "enrolled_at"]


class TeacherEnrollmentSerializer(serializers.ModelSerializer):
    """Enrollment serializer for teachers - shows student details"""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "user",
            "enrolled_at",
            "is_active",
            "unenrolled_at",
        ]
        read_only_fields = ["id", "enrolled_at"]
