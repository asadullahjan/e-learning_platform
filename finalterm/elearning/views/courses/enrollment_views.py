from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from elearning.models import Course, Enrollment
from elearning.permissions import IsCourseOwnerOrEnrollmentOwner
from elearning.serializers import (
    EnrollmentSerializer,
    StudentEnrollmentSerializer,
    TeacherEnrollmentSerializer,
)


class EnrollmentFilter(filters.FilterSet):
    """Custom filter for enrollments"""
    
    # Search filter for username and email
    search = filters.CharFilter(method='filter_search')
    
    # Status filter for active/inactive enrollments
    is_active = filters.BooleanFilter()
    
    # Course filter (already exists)
    course = filters.NumberFilter()
    
    # User filter
    user = filters.NumberFilter()
    
    class Meta:
        model = Enrollment
        fields = ['search', 'is_active', 'course', 'user']
    
    def filter_search(self, queryset, name, value):
        """Search in user username and email fields"""
        if value:
            return queryset.filter(
                user__username__icontains=value
            ) | queryset.filter(
                user__email__icontains=value
            )
        return queryset


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing course enrollments.
    - Students can view their own enrollments with course details
    - Teachers can view enrollments for their courses with student details
    - No individual retrieve action needed (only list views)
    """

    http_method_names = ["get", "post", "put", "patch", "delete"]
    
    # Enable filtering and ordering
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = EnrollmentFilter
    
    # Allow ordering by these fields
    ordering_fields = ['enrolled_at', 'unenrolled_at', 'user__username']
    ordering = ['-enrolled_at']

    def get_queryset(self):
        """
        Return enrollments based on user permissions:
        - Course owners see all enrollments for their courses
        - Non-owners see empty queryset for other courses
        - Users see their own enrollments by default
        """
        user = self.request.user
        course_id = self.request.query_params.get("course")

        if course_id:
            course = get_object_or_404(Course, id=course_id)
            if course.teacher == user:
                # Owner sees all enrollments for this course
                return Enrollment.objects.filter(course=course)
            # Non-owner: return empty queryset (no access)
            return Enrollment.objects.none()

        # Default: return user's own enrollments
        return Enrollment.objects.filter(user=user)

    def get_serializer_class(self):
        """Return appropriate serializer based on user role and context"""
        # Only use role-based serializers for list action
        if self.action != "list":
            return EnrollmentSerializer

        user = self.request.user
        course_id = self.request.query_params.get("course")

        if course_id:
            course = get_object_or_404(Course, id=course_id)
            if course.teacher == user:
                # Teacher viewing enrollments for their course
                return TeacherEnrollmentSerializer

        # User viewing their own enrollments (both students and teachers 
        # can enroll)
        return StudentEnrollmentSerializer

    def get_permissions(self):
        if self.action in ["list"]:
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAuthenticated()]  # Students can enroll
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsCourseOwnerOrEnrollmentOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
