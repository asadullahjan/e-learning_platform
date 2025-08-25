from rest_framework import viewsets

from elearning.models import CourseFeedback
from elearning.permissions import FeedbackPermission
from elearning.serializers import (
    CourseFeedbackCreateUpdateSerializer,
    CourseFeedbackListSerializerForCourse,
)


class FeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = [FeedbackPermission]

    def get_queryset(self):
        course_id = self.kwargs.get("course_pk")
        return CourseFeedback.objects.filter(course_id=course_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs.get("course_pk")
        return context

    def get_serializer_class(self):
        if self.action == "list":
            return CourseFeedbackListSerializerForCourse
        return CourseFeedbackCreateUpdateSerializer

    def perform_create(self, serializer):
        course_id = self.kwargs.get("course_pk")
        serializer.save(
            course_id=course_id,
            user=self.request.user
        )
