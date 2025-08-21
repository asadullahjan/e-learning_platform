from rest_framework import serializers
from elearning.models import StudentRestriction


class StudentRestrictionCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating student restrictions.
    """

    student_id = serializers.IntegerField(write_only=True)
    course_id = serializers.IntegerField(
        required=False, allow_null=True, write_only=True
    )

    # Read-only fields for display
    student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()

    class Meta:
        model = StudentRestriction
        fields = [
            "id",
            "student_id",
            "course_id",
            "reason",
            "student",
            "course",
            "teacher",
            "created_at",
        ]
        read_only_fields = ["id", "student", "course", "teacher", "created_at"]

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
        course_id = data.get("course_id")

        if request and student_id:
            # Check if restriction already exists
            existing = StudentRestriction.objects.filter(
                teacher=request.user,
                student_id=student_id,
                course_id=course_id,
            ).first()

            if existing:
                raise serializers.ValidationError(
                    "Restriction already exists for this student and course"
                )

            # Prevent teachers from restricting themselves
            if student_id == request.user.id:
                raise serializers.ValidationError("Cannot restrict yourself")

        return data

    def get_student(self, obj):
        """Return student information."""
        if obj.student:
            return {
                "id": obj.student.id,
                "username": obj.student.username,
                "email": obj.student.email,
                "role": obj.student.role,
            }
        return None

    def get_course(self, obj):
        """Return course information if applicable."""
        if obj.course:
            return {
                "id": obj.course.id,
                "title": obj.course.title,  # Fixed: using 'title' not 'name'
                "description": obj.course.description,
            }
        return None

    def get_teacher(self, obj):
        """Return teacher information."""
        if obj.teacher:
            return {
                "id": obj.teacher.id,
                "username": obj.teacher.username,
                "email": obj.teacher.email,
                "role": obj.teacher.role,
            }
        return None


class StudentRestrictionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing student restrictions.
    """

    student = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    class Meta:
        model = StudentRestriction
        fields = ["id", "student", "course", "reason", "created_at"]

    def get_student(self, obj):
        """Return student information."""
        if obj.student:
            return {
                "id": obj.student.id,
                "username": obj.student.username,
                "email": obj.student.email,
            }
        return None

    def get_course(self, obj):
        """Return course information if applicable."""
        if obj.course:
            return {
                "id": obj.course.id,
                "title": obj.course.title,  # Fixed: using 'title' not 'name'
                "description": obj.course.description,
            }
        return None
