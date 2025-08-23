from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from elearning.models import Notification
from elearning.serializers.notification_serializers import (
    NotificationSerializer,
)


class NotificationPermission(IsAuthenticated):
    """Custom permission for notifications - users can only see their own"""

    def has_permission(self, request, view):
        # First check if user is authenticated
        if not super().has_permission(request, view):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # Users can only access their own notifications
        return obj.user == request.user


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user notifications.
    Users can only view their own notifications.
    """

    serializer_class = NotificationSerializer
    permission_classes = [NotificationPermission]
    http_method_names = ["get", "patch"]  # Only allow GET and PATCH

    def get_queryset(self):
        """Return only notifications for the current user"""
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["patch"])
    def mark_as_read(self, request, pk=None):
        """Mark a notification as read"""
        updated_count = Notification.objects.filter(
            id=pk, user=request.user
        ).update(is_read=True)

        if updated_count == 0:
            return Response({"error": "Notification not found"}, status=404)

        return Response(
            {"message": "Notification marked as read", "is_read": True}
        )

    @action(detail=False, methods=["patch"])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for the current user"""
        updated_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)

        return Response(
            {"message": f"{updated_count} notifications marked as read"}
        )
