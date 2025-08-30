from django.db.models import Q
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
from elearning.exceptions import ServiceError
from elearning.models import StudentRestriction, Course
from elearning.serializers.courses import (
    CourseStudentRestrictionReadOnlySerializer,
    CourseStudentRestrictionWriteSerializer,
)
from elearning.services.courses import CourseStudentRestrictionService
from elearning.permissions.courses import (
    CourseStudentRestrictionPermission,
)
from django_filters import rest_framework as filters


class CourseStudentRestrictionFilter(filters.FilterSet):
    course = filters.NumberFilter(field_name="course", lookup_expr="exact")

    class Meta:
        model = StudentRestriction
        fields = ["course"]


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
class CourseStudentRestrictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student restrictions.
    Only allows list, create, and delete operations.
    """

    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [CourseStudentRestrictionPermission]
    filterset_class = CourseStudentRestrictionFilter


    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action in ["create", "update", "partial_update"]:
            return CourseStudentRestrictionWriteSerializer
        return CourseStudentRestrictionReadOnlySerializer

    def get_queryset(self):
        """Return restrictions with permission filtering"""
        if getattr(self, "swagger_fake_view", False):
            return StudentRestriction.objects.none()

        # For list actions, use service layer filtering
        if self.action == "list":
            return CourseStudentRestrictionService.get_teacher_restrictions(
                self.request.user
            )

        # For detail actions, return all (service handles )
        return StudentRestriction.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use service for permission checking"""
        restriction_id = kwargs.get("pk")
        instance = CourseStudentRestrictionService.get_restriction_with_permission_check(
            int(restriction_id), request.user
        )
        if not instance:
            raise ServiceError.not_found("Student restriction not found")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=CourseStudentRestrictionWriteSerializer,
        responses={
            201: CourseStudentRestrictionWriteSerializer,
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

        restriction = CourseStudentRestrictionService.create_restriction(
            teacher=self.request.user,
            student=serializer.validated_data.get("student"),
            course=serializer.validated_data.get("course"),
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
        CourseStudentRestrictionService.delete_restriction(
            instance, self.request.user
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Course ID",
            ),
        ],
        responses={
            200: inline_serializer(
                name="RestrictionCheckResultResponse",
                fields={
                    "is_restricted": serializers.BooleanField(
                        help_text="Restriction status"
                    ),
                    "reason": serializers.CharField(
                        help_text="Restriction reason"
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
        Query params: course_id
        """
        course_id = request.query_params.get("course_id")

        if not request.user.id or not course_id:
            return Response(
                {"detail": "course_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, id=int(course_id))

        restriction = StudentRestriction.objects.filter(
            Q(student=request.user, course=course)
            | Q(
                student=request.user,
                teacher=course.teacher,
                course__isnull=True,
            )
        ).first()

        return Response(
            {
                "is_restricted": restriction is not None,
                "reason": restriction.reason if restriction else None,
            }
        )
