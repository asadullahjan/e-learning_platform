"""
Course enrollment serializers for managing student enrollments.

This module contains serializers for creating, updating, and displaying
course enrollments with role-specific functionality.
"""

from rest_framework import serializers
from elearning.models import Enrollment
from elearning.serializers.user_serializers import UserReadOnlySerializer
from elearning.serializers.courses.course_serializers import (
    CourseReadOnlySerializer,
)


class CourseEnrollmentBaseReadOnlySerializer(serializers.ModelSerializer):
    """
    Base serializer for shared enrollment fields.
    """

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "user",
            "enrolled_at",
            "unenrolled_at",
            "is_active",
        ]
        read_only_fields = fields


class CourseEnrollmentReadOnlyForStudentSerializer(
    CourseEnrollmentBaseReadOnlySerializer
):
    """
    Read-only serializer for student enrollment views.
    Includes nested course details only.
    """

    course = CourseReadOnlySerializer()

    class Meta(CourseEnrollmentBaseReadOnlySerializer.Meta):
        read_only_fields = CourseEnrollmentBaseReadOnlySerializer.Meta.fields


class CourseEnrollmentReadOnlyForTeacherSerializer(
    CourseEnrollmentBaseReadOnlySerializer
):
    """
    Read-only serializer for teacher enrollment views.
    Includes nested user details only.
    """

    user = UserReadOnlySerializer()

    class Meta(CourseEnrollmentBaseReadOnlySerializer.Meta):
        read_only_fields = CourseEnrollmentBaseReadOnlySerializer.Meta.fields


class CourseEnrollmentWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating enrollments.

    - `course` comes from URL
    - `user` comes from request.user
    """

    class Meta:
        model = Enrollment
        fields = ["id", "is_active"]
        read_only_fields = ["id"]
