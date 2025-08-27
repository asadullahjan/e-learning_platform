from elearning.models import Course, CourseLesson
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from django.shortcuts import get_object_or_404
from django.http import FileResponse

from elearning.serializers import (
    CourseLessonListSerializer,
    CourseLessonDetailSerializer,
    CourseLessonCreateSerializer,
    CourseLessonUpdateSerializer,
)
from elearning.permissions import (
    IsTeacher,
    IsEnrolledInCourse,
    LessonDownloadPermission,
)
from elearning.services.courses.course_lesson_service import (
    CourseLessonService,
)


@extend_schema(
    tags=["Course Lessons"],
    parameters=[
        OpenApiParameter(
            name="course_pk",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Course ID"
        ),
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Lesson ID"
        ),
    ],
)
class CourseLessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for course lesson operations.
    Teachers can create, update, delete lessons for their courses.
    Students can view lessons for courses they're enrolled in.
    """

    def get_queryset(self):
        user = self.request.user
        course_id = self.kwargs.get("course_pk")

        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return CourseLesson.objects.none()

        if course_id:
            course = get_object_or_404(Course, id=course_id)

            # Teacher sees all lessons (drafts, published, archived)
            if course.teacher == user:
                return CourseLesson.objects.filter(course=course)

            # Students only see published lessons in published courses
            elif (
                user.enrollments.filter(course=course, is_active=True).exists()
                and course.published_at
            ):
                return CourseLesson.objects.filter(
                    course=course,
                    published_at__isnull=False,
                )

            return CourseLesson.objects.none()

    def get_object(self):
        lesson_id = self.kwargs.get("pk")
        if lesson_id:
            lesson = get_object_or_404(CourseLesson, id=lesson_id)
            self.check_object_permissions(self.request, lesson)
            return lesson
        return super().get_object()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        course_id = self.kwargs.get("course_pk")
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            context["course"] = course

        lesson_id = self.kwargs.get("pk")
        if lesson_id:
            lesson = get_object_or_404(CourseLesson, id=lesson_id)
            context["lesson"] = lesson

        return context

    def get_serializer_class(self):
        if self.action == "list":
            return CourseLessonListSerializer
        if self.action == "create":
            return CourseLessonCreateSerializer
        if self.action == "update" or self.action == "partial_update":
            return CourseLessonUpdateSerializer
        return CourseLessonDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsEnrolledInCourse()]
        elif self.action == "download":
            return [LessonDownloadPermission()]
        return [IsTeacher()]

    @extend_schema(
        request=CourseLessonCreateSerializer,
        responses={
            201: CourseLessonDetailSerializer,
            400: inline_serializer(
                name="CourseLessonCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(
                        help_text="Error message"
                    ),
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
                    "file": "file_upload"
                },
                request_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def perform_create(self, serializer):
        course = serializer.context["course"]
        user = self.request.user

        lesson = CourseLessonService.create_lesson_with_file(
            course, serializer.validated_data, user
        )

        return lesson

    @extend_schema(
        request=CourseLessonUpdateSerializer,
        responses={
            200: CourseLessonDetailSerializer,
            400: inline_serializer(
                name="CourseLessonUpdateBadRequestResponse",
                fields={
                    "error": serializers.CharField(
                        help_text="Error message"
                    ),
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
                    "published_at": (
                        "2024-01-01T00:00:00Z"
                    )
                },
                request_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def perform_update(self, serializer):
        user = self.request.user

        # Check if this is a publish/unpublish operation
        if "published_at" in serializer.validated_data:
            lesson = CourseLessonService.toggle_lesson_publish_status(
                serializer.instance, serializer.validated_data["published_at"]
            )
            return lesson

        # Regular update
        lesson = CourseLessonService.update_lesson_with_file(
            serializer.instance, serializer.validated_data, user
        )

        return lesson

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
                    "detail": serializers.CharField(
                        help_text="Error message"
                    ),
                },
            ),
        },
    )
    @action(detail=True, methods=["get"])
    def download(self, request, course_pk=None, pk=None):
        """Download lesson file"""
        lesson = self.get_object()

        if not lesson.file:
            return Response(
                {"detail": "No file available for download"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Return file for download
        file_path = lesson.file.file.path
        filename = lesson.file.original_name

        response = FileResponse(
            open(file_path, "rb"), 
            content_type="application/octet-stream"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        return response
