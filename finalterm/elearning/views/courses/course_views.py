from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from elearning.models import Course
from elearning.permissions import IsTeacher, IsCourseOwner
from elearning.serializers.courses.couses_serializers import (
    CourseSerializer,
    CourseDetailSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for course operations"""

    def get_queryset(self):
        # Everyone can see all courses
        return Course.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            # Anyone can view courses (no authentication required)
            return []
        elif self.action == "create":
            return [IsAuthenticated(), IsTeacher()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsCourseOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
