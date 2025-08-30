from elearning.models import CourseLesson, Course
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from django.http import FileResponse

from elearning.serializers.courses import (
    CourseLessonReadOnlySerializer,
    CourseLessonListReadOnlySerializer,
    CourseLessonWriteSerializer,
)
from elearning.permissions.courses import CourseLessonPermission
from elearning.services.courses.course_lesson_service import (
    CourseLessonService,
)
from elearning.services.courses.course_service import CourseService


@extend_schema(
    tags=["Course Lessons"],
    parameters=[
        OpenApiParameter(
            name="course_pk",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Course ID",
        ),
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Lesson ID",
        ),
    ],
)
class CourseLessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for course lesson operations.
    Teachers can create, update, delete lessons for their courses.
    Students can view lessons for courses they're enrolled in.
    """

    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [CourseLessonPermission]

    def get_queryset(self):
        """Return lessons with permission filtering"""
        # Handle swagger schema generation
        if getattr(self, "swagger_fake_view", False):
            return CourseLesson.objects.none()

        # For list actions, use service layer filtering
        if self.action == "list":
            course_id = self.kwargs.get("course_pk")
            # Use CourseService for consistent course access validation
            course = CourseService.get_course_with_permission_check(
                course_id, self.request.user
            )
            return CourseLessonService.get_lessons_for_course(
                course, self.request.user
            )

        # For detail actions, return all (service handles 403 vs 404)
        return CourseLesson.objects.all()

    def get_serializer_class(self):
        if self.action in ["list"]:
            return CourseLessonListReadOnlySerializer
        if self.action in ["create", "update", "partial_update"]:
            return CourseLessonWriteSerializer
        return CourseLessonReadOnlySerializer

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use service for permission checking"""
        lesson_id = kwargs.get("pk")
        instance = CourseLessonService.get_lesson_with_permission_check(
            lesson_id, request.user
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=CourseLessonWriteSerializer,
        responses={
            201: CourseLessonWriteSerializer,
            400: inline_serializer(
                name="CourseLessonCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Create Lesson",
                value={
                    "title": "Introduction to Python",
                    "description": "Learn the basics of Python programming",
                    "content": "Python programming basics...",
                    "file": "file_upload",
                },
                request_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def perform_create(self, serializer):
        course_id = self.kwargs.get("course_pk")
        # Get course object - no need for permission check here since
        # lesson creation is controlled by user role (teacher only)
        course = get_object_or_404(Course, id=course_id)
        user = self.request.user
        file_data = self.request.FILES.get("file")

        lesson = CourseLessonService.create_lesson_with_file(
            course, user, serializer.validated_data, file_data
        )

        serializer.instance = lesson

    @extend_schema(
        request=CourseLessonWriteSerializer,
        responses={
            200: CourseLessonWriteSerializer,
            400: inline_serializer(
                name="CourseLessonUpdateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Update Lesson",
                value={
                    "title": "Updated Python Introduction",
                    "description": "Updated description",
                    "content": "Updated content...",
                    "published_at": ("2024-01-01T00:00:00Z"),
                },
                request_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def perform_update(self, serializer):
        user = self.request.user
        lesson_data = serializer.validated_data.copy()
        file_data = self.request.FILES.get("file")

        # Handle publish/unpublish
        published_at = lesson_data.pop("published_at", None)
        lesson = serializer.instance
        if published_at is not None:
            lesson = CourseLessonService.toggle_lesson_publish_status(
                lesson, published_at
            )

        # Handle normal update with remaining fields
        lesson = CourseLessonService.update_lesson_with_file(
            lesson, lesson_data, user, file_data
        )

        serializer.instance = lesson

    @extend_schema(
        responses={
            204: None,
        },
    )
    def perform_destroy(self, instance):
        user = self.request.user

        CourseLessonService.delete_lesson_with_file(instance, user)

    @extend_schema(
        responses={
            200: inline_serializer(
                name="FileDownloadResponse",
                fields={
                    "file_content": serializers.CharField(
                        help_text="Binary file content"
                    ),
                },
            ),
            404: inline_serializer(
                name="FileNotFoundResponse",
                fields={
                    "detail": serializers.CharField(help_text="Error message"),
                },
            ),
        },
    )
    @action(detail=True, methods=["get"])
    def download(self, request, course_pk=None, pk=None):
        """Download lesson file"""
        # Use service layer for proper permission checking
        lesson_id = pk
        file_obj = CourseLessonService.get_lesson_file_with_permission_check(
            int(lesson_id), request.user
        )

        # Return file for download
        file_path = file_obj.file.path
        filename = file_obj.original_name

        with open(file_path, "rb") as f:
            response = FileResponse(f, content_type="application/octet-stream")
            response["Content-Disposition"] = (
                f'attachment; filename="{filename}"'
            )
            return response
