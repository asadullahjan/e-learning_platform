from rest_framework import viewsets, permissions

from elearning.models import Course, CourseFeedback
from elearning.serializers import (
    CourseFeedbackCreateUpdateSerializer,
    CourseFeedbackListSerializerForCourse,
)


class FeedbackPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view feedback
        
        # Must be logged in to create/edit
        if not request.user.is_authenticated:
            return False
            
        # For create/update/delete, check if user is enrolled
        course_id = view.kwargs.get("course_pk")
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                # Check if user is actively enrolled
                if not course.enrollments.filter(
                    user=request.user, 
                    is_active=True
                ).exists():
                    return False
            except Course.DoesNotExist:
                return False
        
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True  # Anyone can view feedback
        return obj.user == request.user  # Only owner can edit/delete


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
