from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from elearning.models import Course, Enrollment
from elearning.permissions.courses.enrollment_permissions import (
    EnrollmentPermission,
)
from elearning.serializers import (
    EnrollmentSerializer,
    StudentEnrollmentSerializer,
    TeacherEnrollmentSerializer,
)


class EnrollmentFilter(filters.FilterSet):
    """Custom filter for enrollments"""

    # Search filter for username and email
    search = filters.CharFilter(method="filter_search")

    # Status filter for active/inactive enrollments
    is_active = filters.BooleanFilter()

    # User filter
    user = filters.NumberFilter()

    class Meta:
        model = Enrollment
        fields = ["search", "is_active", "user"]

    def filter_search(self, queryset, name, value):
        """Search in user username and email fields"""
        if value:
            return queryset.filter(
                user__username__icontains=value
            ) | queryset.filter(user__email__icontains=value)
        return queryset


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments within a specific course.
    - Teachers can see all enrollments for their course
    - Students can enroll/unenroll themselves
    - All operations are scoped to the specific course
    """

    http_method_names = ["get", "post", "delete"]
    serializer_class = EnrollmentSerializer
    permission_classes = [EnrollmentPermission]

    def get_queryset(self):
        """Return enrollments for the specific course"""
        course_id = self.kwargs.get("course_pk")
        try:
            course = Course.objects.get(id=course_id)
            # Teachers see all enrollments, students see only their own
            if course.teacher == self.request.user:
                return Enrollment.objects.filter(course=course)
            else:
                return Enrollment.objects.filter(
                    course=course, user=self.request.user
                )
        except Course.DoesNotExist:
            return Enrollment.objects.none()

    def get_serializer_class(self):
        """Return appropriate serializer based on user role"""
        if self.action == "list":
            course_id = self.kwargs.get("course_pk")
            try:
                course = Course.objects.get(id=course_id)
                if course.teacher == self.request.user:
                    return TeacherEnrollmentSerializer
            except Course.DoesNotExist:
                pass
        return EnrollmentSerializer

    def perform_create(self, serializer):
        """Create enrollment for the specific course"""
        from ...services.courses.enrollment_service import EnrollmentService

        course_id = self.kwargs.get("course_pk")
        course = Course.objects.get(id=course_id)

        # Use service layer to create enrollment
        enrollment = EnrollmentService.enroll_student(
            course, self.request.user
        )

        serializer.instance = enrollment


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for users to view their own enrollments.
    - Read-only view of user's enrolled courses
    - No course-specific filtering needed
    """

    serializer_class = StudentEnrollmentSerializer
    permission_classes = [EnrollmentPermission]
    filter_backends = [OrderingFilter]
    ordering_fields = ["enrolled_at", "unenrolled_at"]
    ordering = ["-enrolled_at"]

    def get_queryset(self):
        """Return user's own enrollments"""
        return Enrollment.objects.filter(user=self.request.user)
