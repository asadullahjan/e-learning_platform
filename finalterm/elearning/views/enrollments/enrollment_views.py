from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from elearning.models import Enrollment
from elearning.permissions import IsCourseOwner
from elearning.serializers.enrollments import EnrollmentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()

    def get_serializer_class(self):
        return EnrollmentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), IsCourseOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
