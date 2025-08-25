from elearning.models import Course, CourseLesson
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

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
    LessonDownloadPermission,
    IsEnrolledInCourse,
)
from elearning.services.courses.course_lesson_service import (
    CourseLessonService,
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

    def perform_create(self, serializer):
        course = serializer.context["course"]
        user = self.request.user

        lesson = CourseLessonService.create_lesson_with_file(
            course, serializer.validated_data, user
        )

        return lesson

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

    def perform_destroy(self, instance):
        user = self.request.user

        CourseLessonService.delete_lesson_with_file(instance, user)

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
            open(file_path, "rb"), content_type="application/octet-stream"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
