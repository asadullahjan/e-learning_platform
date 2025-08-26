from rest_framework import viewsets

from elearning.models import Course
from elearning.permissions import CourseFeedbackPermission
from elearning.serializers import (
    CourseFeedbackCreateUpdateSerializer,
    CourseFeedbackListSerializerForCourse,
)
from elearning.services.courses.course_feedback_service import (
    CourseFeedbackService,
)


class FeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [CourseFeedbackPermission]

    def get_queryset(self):
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

    def perform_update(self, serializer):
        # ✅ CORRECT: ServiceError handled automatically by custom
        # exception handler
        feedback = CourseFeedbackService.update_feedback(
            feedback=serializer.instance,
            user=self.request.user,
            **serializer.validated_data,
        )
        serializer.instance = feedback

    def perform_destroy(self, instance):
        # ✅ CORRECT: ServiceError handled automatically by custom
        # exception handler
        CourseFeedbackService.delete_feedback(
            feedback=instance, user=self.request.user
        )
