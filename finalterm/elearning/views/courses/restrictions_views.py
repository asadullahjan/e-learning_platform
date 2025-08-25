from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from elearning.serializers.courses.student_restriction_serializer import (
    StudentRestrictionCreateUpdateSerializer,
    StudentRestrictionListSerializer,
)
from elearning.permissions import StudentRestrictionPermission
from elearning.services.courses.student_restriction_service import (
    StudentRestrictionService,
)


class StudentRestrictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student restrictions.
    Only allows list, create, and delete operations.
    """

    permission_classes = [StudentRestrictionPermission]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        """Return restrictions created by the current teacher."""
        return StudentRestrictionService.get_teacher_restrictions(
            self.request.user
        )

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return StudentRestrictionListSerializer
        return StudentRestrictionCreateUpdateSerializer

    def perform_create(self, serializer):
        """Create restriction using the service."""
        try:
            restriction = StudentRestrictionService.create_restriction(
                teacher=self.request.user,
                student_id=serializer.validated_data["student_id"],
                course_id=serializer.validated_data.get("course_id"),
                reason=serializer.validated_data.get("reason", ""),
            )
            # Update serializer instance for response
            serializer.instance = restriction
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def perform_destroy(self, instance):
        """Delete restriction using the service."""
        StudentRestrictionService.delete_restriction(instance)

    @action(detail=False, methods=["get"])
    def check_student(self, request):
        """
        Check if a specific student is restricted.
        Query params: student_id, course_id (optional)
        """
        student_id = request.query_params.get("student_id")
        course_id = request.query_params.get("course_id")

        if not student_id:
            return Response(
                {"detail": "student_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from elearning.models import User, Course

            student = get_object_or_404(User, id=student_id)
            course = None

            if course_id:
                course = get_object_or_404(Course, id=course_id)

            is_restricted = StudentRestrictionService.is_student_restricted(
                student, request.user, course
            )

            return Response(
                {
                    "student_id": student_id,
                    "course_id": course_id,
                    "is_restricted": is_restricted,
                }
            )

        except (User.DoesNotExist, Course.DoesNotExist):
            return Response(
                {"detail": "Student or course not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
