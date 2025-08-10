from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from elearning.models import Course, Enrollment
from elearning.permissions import IsCourseOwnerOrEnrollmentOwner
from elearning.serializers.enrollments import EnrollmentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
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
