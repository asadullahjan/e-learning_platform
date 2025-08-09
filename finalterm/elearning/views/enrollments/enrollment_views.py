from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response
from elearning.models import Course, Enrollment
from elearning.permissions import IsCourseOwnerOrEnrollmentOwner
from elearning.serializers.enrollments import EnrollmentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        """
        This only runs when returning lists of enrollments (course owner case)
        or a user's own enrollments.
        """
        user = self.request.user
        course_id = self.request.query_params.get("course")

        if course_id:
            course = get_object_or_404(Course, id=course_id)
            if course.teacher == user:
                # Owner sees all enrollments for this course
                return Enrollment.objects.filter(course=course)
            # Non-owner: we'll handle count response in list(), so
            # return empty queryset here
            return Enrollment.objects.none()

        # Default: return user's own enrollments
        return Enrollment.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        """
        Override list() so non-owners get count instead of empty list.
        """
        course_id = request.query_params.get("course")
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            if course.teacher != request.user:
                count = Enrollment.objects.filter(
                    course=course, is_active=True
                ).count()
                total_enrollments = Enrollment.objects.filter(
                    course=course
                ).count()
                return Response(
                    {
                        "course": course_id,
                        "active_enrollments": count,
                        "total_enrollments": total_enrollments,
                    }
                )
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        return EnrollmentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAuthenticated()]  # Students can enroll
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsCourseOwnerOrEnrollmentOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
