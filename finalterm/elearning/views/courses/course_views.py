from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from elearning.models import Course
from elearning.permissions.courses.course_permissions import CoursePermission
from elearning.serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
)
from elearning.services.courses.course_service import CourseService


class CourseFilter(filters.FilterSet):
    # Custom filter for teachers to filter by publication status
    publication_status = filters.ChoiceFilter(
        choices=[
            ("published", "Published"),
            ("unpublished", "Unpublished"),
            ("all", "All"),
        ],
        method="filter_by_publication_status",
    )

    title = filters.CharFilter(lookup_expr="icontains")
    description = filters.CharFilter(lookup_expr="icontains")
    teacher__username = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Course
        fields = ["publication_status", "teacher", "title", "description"]

    def filter_by_publication_status(self, queryset, name, value):
        if value == "published":
            return queryset.filter(published_at__isnull=False)
        elif value == "unpublished":
            return queryset.filter(published_at__isnull=True)
        elif value == "all":
            return queryset  # Return all courses
        return queryset


@extend_schema(
    tags=["Courses"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Course ID",
        ),
    ],
)
class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for course operations"""

    # Enable built-in filtering, search, ordering
    filter_backends = [OrderingFilter, DjangoFilterBackend]

    # Allow ordering by these fields
    ordering_fields = ["published_at"]
    ordering = ["-published_at"]

    # Add the custom filter
    filterset_class = CourseFilter
    permission_classes = [CoursePermission]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        elif self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        # For list actions, filter by permissions
        if self.action == "list":
            return CourseService.get_courses_for_user(self.request.user)
        # For detail actions (retrieve, update, delete), get all courses
        # Permission checks will be done in service layer to return proper 403
        return Course.objects.all()

    @extend_schema(
        request=CourseSerializer,
        responses={
            201: CourseDetailSerializer,
            400: inline_serializer(
                name="CourseCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Create Course",
                value={
                    "title": "Web Development Intro",
                    "description": "Learn web development fundamentals",
                    "published_at": "2024-01-01T00:00:00Z",
                },
                request_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def perform_create(self, serializer):
        # ✅ CORRECT: Delegate to service
        course = CourseService.create_course_with_chat(
            teacher=self.request.user, course_data=serializer.validated_data
        )

        # Populate computed fields before setting instance
        course = CourseService.populate_course_computed_fields(
            course, self.request.user
        )
        serializer.instance = course

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use service for permission checking"""
        course_id = kwargs.get("pk")
        instance = CourseService.get_course_with_permission_check(
            int(course_id), request.user
        )
        # Populate computed fields before serialization
        instance = CourseService.populate_course_computed_fields(
            instance, request.user
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """Override update to use service layer for permission checks"""
        instance = serializer.instance
        CourseService.update_course(
            instance, serializer.validated_data, self.request.user
        )
        instance = CourseService.populate_course_computed_fields(
            instance, self.request.user
        )
        serializer.instance = instance

    def perform_destroy(self, instance):
        """Override destroy to use service layer for permission checks"""
        CourseService.delete_course(instance, self.request.user)
