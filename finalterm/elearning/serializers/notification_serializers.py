"""
Notification serializers for updating, and displaying notifications
"""

from rest_framework import serializers
from elearning.models import Notification


class NotificationReadOnlySerializer(serializers.ModelSerializer):
    """
    Notification serializer for displaying notifications.

    Shows notification content with read status and
    action information for user notification views.
    """

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "action_url",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields