from rest_framework import serializers
from typing import Optional, Dict, Any
from drf_spectacular.utils import extend_schema_field
from elearning.serializers.user_serializers import UserSerializer
from elearning.serializers.courses.course_serializers import CourseSerializer
from elearning.models import StudentRestriction


class StudentRestrictionCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating student restrictions.
    INPUT ONLY - Frontend sends IDs
    """

    # Explicitly declare the ID fields for input
    student_id = serializers.IntegerField(write_only=True)
    course_id = serializers.IntegerField(
        write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = StudentRestriction
        fields = ["student_id", "course_id", "reason"]

    def validate_student_id(self, value):
        """Validate that the student_id is a positive integer."""
        if not isinstance(value, int) or value <= 0:
            raise serializers.ValidationError(
                "Student ID must be a positive integer"
            )
        return value

    def validate_course_id(self, value):
        """Validate that the course_id is a positive integer if provided."""
        if value is not None:
            if not isinstance(value, int) or value <= 0:
                raise serializers.ValidationError(
                    "Course ID must be a positive integer"
                )
        return value

    def validate(self, data):
        """Validate the restriction data."""
        request = self.context.get("request")
        student_id = data.get("student_id")

        if request and student_id:
            # ✅ CORRECT: Only validation logic, no database queries
            if student_id == request.user.id:
                raise serializers.ValidationError(
                    {"student_id": ["Cannot restrict yourself"]}
                )

        return data

    def to_representation(self, instance):
        """Use read serializer for response representation"""
        return StudentRestrictionDetailSerializer(
            instance, context=self.context
        ).data


class StudentRestrictionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed view of student restrictions.
    OUTPUT ONLY - Returns full objects
    """

    student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()

    class Meta:
        model = StudentRestriction
        fields = ["id", "student", "course", "teacher", "reason", "created_at"]

    @extend_schema_field(UserSerializer)
    def get_student(self, obj) -> Optional[Dict[str, Any]]:
        """Return student information using UserSerializer."""
        if obj.student:
            return UserSerializer(obj.student).data
        return None

    @extend_schema_field(CourseSerializer)
    def get_course(self, obj) -> Optional[Dict[str, Any]]:
        """Return course information using CourseSerializer."""
        if obj.course:
            return CourseSerializer(obj.course).data
        return None

    @extend_schema_field(UserSerializer)
    def get_teacher(self, obj) -> Optional[Dict[str, Any]]:
        """Return teacher information using UserSerializer."""
        if obj.teacher:
            return UserSerializer(obj.teacher).data
        return None


class StudentRestrictionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing student restrictions.
    OUTPUT ONLY - Returns full objects
    """

    student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    class Meta:
        model = StudentRestriction
        fields = ["id", "student", "course", "reason", "created_at"]

    @extend_schema_field(UserSerializer)
    def get_student(self, obj):
        """Return student information using UserSerializer."""
        if obj.student:
            return UserSerializer(obj.student).data
        return None

    @extend_schema_field(CourseSerializer)
    def get_course(self, obj):
        """Return course information using CourseSerializer."""
        if obj.course:
            return CourseSerializer(obj.course).data
        return None
