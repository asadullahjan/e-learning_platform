from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

from ..models import ChatRoom, ChatParticipant, Course
from ..permissions import IsTeacher, IsCourseOwner
from ..serializers import (
    CourseSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
)


class CourseFilter(filters.FilterSet):
    # Custom filter for teachers to filter by publication status
    publication_status = filters.ChoiceFilter(
        choices=[
            ("published", "Published"),
            ("unpublished", "Unpublished"),
            ("all", "All"),
        ],
        method="filter_by_publication_status",
    )

    title = filters.CharFilter(lookup_expr="icontains")
    description = filters.CharFilter(lookup_expr="icontains")
    teacher__username = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Course
        fields = ["publication_status", "teacher", "title", "description"]

    def filter_by_publication_status(self, queryset, name, value):
        if value == "published":
            return queryset.filter(published_at__isnull=False)
        elif value == "unpublished":
            return queryset.filter(published_at__isnull=True)
        elif value == "all":
            return queryset  # Return all courses
        return queryset


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for course operations"""

    # Enable built-in filtering, search, ordering
    filter_backends = [OrderingFilter, DjangoFilterBackend]

    # Allow ordering by these fields
    ordering_fields = ["published_at"]
    ordering = ["-published_at"]

    # Add the custom filter
    filterset_class = CourseFilter

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

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            # Start with published courses
            queryset = Course.objects.filter(published_at__isnull=False)

            # If user is a teacher, also include their own courses
            if (
                self.request.user.is_authenticated
                and self.request.user.role == "teacher"
            ):
                user_courses = Course.objects.filter(teacher=self.request.user)
                queryset = (queryset | user_courses).distinct()

            return queryset

        # For other actions (create, update, delete), show all courses
        return Course.objects.all()

    def perform_create(self, serializer):
        # First save the course
        course = serializer.save(teacher=self.request.user)

        # Create the chatroom for the course
        chatroom = ChatRoom.objects.create(
            name=f"{course.title} Chat",
            course=course,
            chat_type="course",
            is_public=True,
            created_by=self.request.user,
        )

        # Add the course creator as admin participant
        ChatParticipant.objects.create(
            chat_room=chatroom, user=self.request.user, role="admin"
        )
