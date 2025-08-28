from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, inline_serializer
)
from drf_spectacular.types import OpenApiTypes
from elearning.models import Course, Enrollment
from elearning.permissions.courses.enrollment_permissions import (
    EnrollmentPermission,
)
from elearning.serializers import (
    EnrollmentSerializer,
    StudentEnrollmentSerializer,
    TeacherEnrollmentSerializer,
)
from rest_framework import serializers
from elearning.services.courses.enrollment_service import EnrollmentService


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


@extend_schema(
    tags=["Course Enrollments"],
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
            description="Enrollment ID"
        ),
    ],
)
class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments within a specific course.
    - Teachers can see all enrollments for their course
    - Students can enroll/activate/deactivate their enrollment
    - Teachers can activate/deactivate student enrollments
    - All operations are scoped to the specific course
    """

    http_method_names = ["get", "post", "patch", "put"]
    permission_classes = [EnrollmentPermission]

    def get_queryset(self):
        """Return enrollments with permission filtering"""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Enrollment.objects.none()

        course_id = self.kwargs.get("course_pk")
        if not course_id:
            return Enrollment.objects.none()

        try:
            course = Course.objects.get(id=course_id)
            qs = EnrollmentService.get_enrollments_for_course(course, self.request.user)
        except Course.DoesNotExist:
            return Enrollment.objects.none()

        # Optimize based on user role
        if self.request.user.role == "teacher":
            # Teachers need user data for all enrollments in their course
            return qs.select_related("user")
        else:  # student
            # Students only see their own enrollment, no need for user data
            return qs.select_related("course", "course__teacher")

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

    @extend_schema(
        responses={
            201: EnrollmentSerializer,
            400: inline_serializer(
                name="EnrollmentCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(
                        help_text="Error message"
                    ),
                },
            ),
        },
    )
    def perform_create(self, serializer):
        """Create enrollment for the specific course"""

        course_id = self.kwargs.get("course_pk")
        course = Course.objects.get(id=course_id)

        # Use service layer to create enrollment
        enrollment = EnrollmentService.enroll_student(
            course, self.request.user
        )

        serializer.instance = enrollment

    def perform_update(self, serializer):
        """Update enrollment (activate/deactivate) using service layer"""
        
        # Use service layer to modify enrollment
        enrollment = EnrollmentService.modify_enrollment(
            serializer.instance, self.request.user, **serializer.validated_data
        )
        serializer.instance = enrollment


@extend_schema(
    tags=["User Enrollments"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Enrollment ID"
        ),
    ],
)
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
        return Enrollment.objects.select_related(
            'course', 'course__teacher'
        ).filter(user=self.request.user)
