from rest_framework import viewsets
from django_filters import rest_framework as filters
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import IsAuthenticated
from elearning.models import Course, Enrollment
from elearning.permissions.courses import (
    CourseEnrollmentPermission,
    CourseEnrollmentPolicy,
)
from elearning.serializers.courses import (
    CourseEnrollmentReadOnlyForStudentSerializer,
    CourseEnrollmentReadOnlyForTeacherSerializer,
    CourseEnrollmentWriteSerializer,
)
from rest_framework import serializers
from elearning.services.courses import CourseEnrollmentService
from elearning.exceptions import ServiceError


class CourseEnrollmentFilter(filters.FilterSet):
    """Custom filter for enrollments"""

    is_active = filters.BooleanFilter()
    user = filters.NumberFilter()

    class Meta:
        model = Enrollment
        fields = ["is_active", "user"]


@extend_schema(
    tags=["Course Enrollments"],
    parameters=[
        OpenApiParameter(
            name="course_pk",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Course ID",
        ),
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Enrollment ID",
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

    http_method_names = ["get", "post", "patch"]
    permission_classes = [CourseEnrollmentPermission]
    filterset_class = CourseEnrollmentFilter
    ordering = ["-enrolled_at"]
    ordering_fields = ["enrolled_at", "unenrolled_at"]
    search_fields = ["user__username", "user__email"]

    def get_course(self):
        """Get course once and cache it for the request"""
        if not hasattr(self, "_course"):
            course_id = self.kwargs.get("course_pk")
            try:
                self._course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                raise ServiceError.not_found("Course not found")
        return self._course

    def get_queryset(self):
        """Return enrollments with permission filtering"""
        # Handle swagger schema generation
        if getattr(self, "swagger_fake_view", False):
            return Enrollment.objects.none()

        qs = CourseEnrollmentService.get_enrollments_for_course(
            self.get_course(), self.request.user
        )

        # Optimize based on user role
        if self.request.user.role == "teacher":
            # Teachers need user data for all enrollments in their course
            return qs.select_related("user")
        else:  # student
            # Students only see their own enrollment, no need for user data
            return qs.select_related("course", "course__teacher")

    def get_serializer_class(self):
        """Return appropriate serializer based on user role"""
        if self.action in ["list", "retrieve"]:
            return CourseEnrollmentReadOnlyForTeacherSerializer
        return CourseEnrollmentWriteSerializer

    def retrieve(self, request, *args, **kwargs):
        """Check if student is restricted before retrieving enrollment"""
        enrollment = super().retrieve(request, *args, **kwargs)
        if request.user.role == "student":
            CourseEnrollmentPolicy.check_can_view_enrollment(
                request.user, enrollment, raise_exception=True
            )
        return enrollment

    @extend_schema(
        responses={
            201: CourseEnrollmentWriteSerializer,
            400: inline_serializer(
                name="EnrollmentCreateBadRequestResponse",
                fields={
                    "error": serializers.CharField(help_text="Error message"),
                },
            ),
        },
    )
    def perform_create(self, serializer):
        """Create enrollment for the specific course"""
        # Use service layer to create enrollment
        enrollment = CourseEnrollmentService.enroll_student(
            self.get_course(), self.request.user
        )
        serializer.instance = enrollment

    def perform_update(self, serializer):
        """Update enrollment (activate/deactivate) using service layer"""
        # Use service layer to modify enrollment
        enrollment = CourseEnrollmentService.modify_enrollment(
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
            description="Enrollment ID",
        ),
    ],
)
class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for users to view their own enrollments.
    - Read-only view of user's enrolled courses
    - No course-specific filtering needed
    """

    serializer_class = CourseEnrollmentReadOnlyForStudentSerializer
    permission_classes = [IsAuthenticated]
    ordering = ["-enrolled_at"]

    def get_queryset(self):
        """Return user's own enrollments"""
        return Enrollment.objects.select_related(
            "course", "course__teacher"
        ).filter(user=self.request.user)
