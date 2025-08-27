from rest_framework import viewsets
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiExample, inline_serializer
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from elearning.models import Course, CourseFeedback
from elearning.permissions import CourseFeedbackPermission
from elearning.serializers import (
    CourseFeedbackCreateUpdateSerializer,
    CourseFeedbackListSerializerForCourse,
)
from elearning.services.courses.course_feedback_service import (
    CourseFeedbackService,
)


@extend_schema(
    tags=["Course Feedback"],
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
            description="Feedback ID"
        ),
    ],
)
class FeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [CourseFeedbackPermission]

    def get_queryset(self):
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return CourseFeedback.objects.none()
            
        course_id = self.kwargs.get("course_pk")
        course = Course.objects.get(id=course_id)
        return CourseFeedbackService.get_course_feedback(course)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs.get("course_pk")
        return context

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
                    "error": serializers.CharField(
                        help_text="Error message"
                    ),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Create Feedback",
                value={
                    "rating": 5,
                    "text": "Great course! Very informative."
                },
                request_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def perform_create(self, serializer):
        # ✅ CORRECT: ServiceError handled automatically by custom
        # exception handler
        course_id = self.kwargs.get("course_pk")
        course = Course.objects.get(id=course_id)

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
                    "error": serializers.CharField(
                        help_text="Error message"
                    ),
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Update Feedback",
                value={
                    "rating": 4,
                    "text": "Updated feedback text"
                },
                request_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def perform_update(self, serializer):
        # ✅ CORRECT: ServiceError handled automatically by custom
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
        # ✅ CORRECT: ServiceError handled automatically by custom
        # exception handler
        CourseFeedbackService.delete_feedback(
            feedback=instance, user=self.request.user
        )
