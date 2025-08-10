from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from elearning.models import Course
from elearning.permissions import IsTeacher, IsCourseOwner
from elearning.serializers.courses import (
    CourseSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for course operations"""

    queryset = Course.objects.filter(published_at__isnull=False)

    # Enable built-in filtering, search, ordering
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]

    # Search across multiple fields
    search_fields = ["title", "description", "teacher__username"]

    # Allow ordering by these fields
    ordering_fields = ["published_at"]
    ordering = ["-published_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        elif self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            # Anyone can view courses (no authentication required)
            return [AllowAny()]
        elif self.action == "create":
            return [IsAuthenticated(), IsTeacher()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsCourseOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
