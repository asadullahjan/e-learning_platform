from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers
from elearning.models import StudentRestriction
from elearning.serializers.courses.student_restriction_serializer import (
    StudentRestrictionCreateUpdateSerializer,
    StudentRestrictionDetailSerializer,
    StudentRestrictionListSerializer,
)
from elearning.services.courses.student_restriction_service import (
    StudentRestrictionService,
)


@extend_schema(
    tags=["Student Restrictions"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Restriction ID",
        ),
    ],
)
class StudentRestrictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student restrictions.
    Only allows list, create, and delete operations.
    """

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action in ["create", "update", "partial_update"]:
            return StudentRestrictionCreateUpdateSerializer
        elif self.action == "retrieve":
            return StudentRestrictionDetailSerializer
        else:
            return StudentRestrictionListSerializer

    def get_queryset(self):
        """Return restrictions with permission filtering"""
        if getattr(self, "swagger_fake_view", False):
            return StudentRestriction.objects.none()

        # For list actions, use service layer filtering
        if self.action == "list":
            return StudentRestrictionService.get_teacher_restrictions(
                self.request.user
            )

        # For detail actions, return all (service handles 403 vs 404)
        return StudentRestriction.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use service for permission checking"""
        restriction_id = kwargs.get("pk")
        instance = (
            StudentRestrictionService.get_restriction_with_permission_check(
                int(restriction_id), request.user
            )
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=StudentRestrictionCreateUpdateSerializer,
        responses={
            201: StudentRestrictionDetailSerializer,
            400: inline_serializer(
                name="StudentRestrictionCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Create Restriction",
                value={
                    "student_id": 1,
                    "course_id": 1,
                    "reason": "Academic misconduct",
                },
                request_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def perform_create(self, serializer):
        """Create restriction using the service."""
        # ✅ CORRECT: ServiceError handled automatically by custom
        # exception handler
        restriction = StudentRestrictionService.create_restriction(
            teacher=self.request.user,
            student_id=serializer.validated_data["student_id"],
            course_id=serializer.validated_data.get("course_id"),
            reason=serializer.validated_data.get("reason", ""),
        )
        # Update serializer instance for response
        serializer.instance = restriction

    @extend_schema(
        responses={
            204: None,
        },
    )
    def perform_destroy(self, instance):
        """Delete restriction using the service."""
        StudentRestrictionService.delete_restriction(instance)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="student_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Student ID to check",
            ),
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Course ID (optional)",
            ),
        ],
        responses={
            200: inline_serializer(
                name="RestrictionCheckResultResponse",
                fields={
                    "student_id": serializers.IntegerField(
                        help_text="Student ID"
                    ),
                    "course_id": serializers.IntegerField(
                        help_text="Course ID (optional)"
                    ),
                    "is_restricted": serializers.BooleanField(
                        help_text="Restriction status"
                    ),
                },
            ),
            400: inline_serializer(
                name="RestrictionCheckBadRequestResponse",
                fields={
                    "detail": serializers.CharField(help_text="Error message"),
                },
            ),
            404: inline_serializer(
                name="RestrictionCheckNotFoundResponse",
                fields={
                    "detail": serializers.CharField(help_text="Error message"),
                },
            ),
        },
    )
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
