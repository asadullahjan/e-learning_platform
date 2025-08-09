from elearning.models import Enrollment
from rest_framework import serializers


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "course", "user", "enrolled_at"]
        read_only_fields = ["id", "user", "enrolled_at"]
