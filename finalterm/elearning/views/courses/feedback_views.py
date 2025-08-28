from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from elearning.models import CourseFeedback, Course
from elearning.permissions import CourseFeedbackPermission
from elearning.serializers import (
    CourseFeedbackCreateUpdateSerializer,
    CourseFeedbackListSerializerForCourse,
)
from elearning.services.courses.course_feedback_service import (
    CourseFeedbackService,
)
from elearning.services.courses.course_service import CourseService


@extend_schema(
    tags=["Course Feedback"],
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
            description="Feedback ID",
        ),
    ],
)
class FeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [CourseFeedbackPermission]

    def get_queryset(self):
        """Return feedback with permission filtering"""
        # Handle swagger schema generation
        if getattr(self, "swagger_fake_view", False):
            return CourseFeedback.objects.none()

        # For list actions, use service layer filtering
        if self.action == "list":
            course_id = self.kwargs.get("course_pk")
            if course_id:
                try:
                    # Use CourseService for consistent course access validation
                    course = CourseService.get_course_with_permission_check(
                        int(course_id), self.request.user
                    )
                    return CourseFeedbackService.get_course_feedback(course)
                except Exception:
                    return CourseFeedback.objects.none()
            return CourseFeedback.objects.none()

        # For detail actions, return all (service handles 403 vs 404)
        return CourseFeedback.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use service for permission checking"""
        feedback_id = kwargs.get("pk")
        instance = CourseFeedbackService.get_feedback_with_permission_check(
            int(feedback_id), request.user
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "list":
            return CourseFeedbackListSerializerForCourse
        return CourseFeedbackCreateUpdateSerializer

    @extend_schema(
        request=CourseFeedbackCreateUpdateSerializer,
        responses={
            201: CourseFeedbackCreateUpdateSerializer,
            400: inline_serializer(
                name="CourseFeedbackCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Create Feedback",
                value={"rating": 5, "text": "Great course! Very informative."},
                request_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def perform_create(self, serializer):
        course_id = self.kwargs.get("course_pk")
        # Get course object - no need for permission check here since 
        # feedback creation is controlled by chat participation
        course = get_object_or_404(Course, id=course_id)

        feedback = CourseFeedbackService.create_feedback(
            user=self.request.user,
            course=course,
            rating=serializer.validated_data["rating"],
            text=serializer.validated_data["text"],
        )

        serializer.instance = feedback

    @extend_schema(
        request=CourseFeedbackCreateUpdateSerializer,
        responses={
            200: CourseFeedbackCreateUpdateSerializer,
            400: inline_serializer(
                name="CourseFeedbackUpdateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Update Feedback",
                value={"rating": 4, "text": "Updated feedback text"},
                request_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def perform_update(self, serializer):
        # ServiceError handled automatically by custom
        # exception handler
        feedback = CourseFeedbackService.update_feedback(
            feedback=serializer.instance,
            user=self.request.user,
            **serializer.validated_data,
        )
        serializer.instance = feedback

    @extend_schema(
        responses={
            204: None,
        },
    )
    def perform_destroy(self, instance):
        # ServiceError handled automatically by custom
        # exception handler
        CourseFeedbackService.delete_feedback(
            feedback=instance, user=self.request.user
        )
