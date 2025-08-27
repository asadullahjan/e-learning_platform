from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from elearning.models import Notification
from elearning.permissions import NotificationPermission
from elearning.serializers.notification_serializers import (
    NotificationSerializer,
)


@extend_schema(
    tags=["Notifications"],
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Notification ID",
        ),
    ],
)
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
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @extend_schema(
        responses={
            200: inline_serializer(
                name="NotificationMarkedAsReadResponse",
                fields={
                    "message": serializers.CharField(
                        help_text="Success message"
                    ),
                    "is_read": serializers.BooleanField(
                        help_text="Read status"
                    ),
                },
            ),
            404: inline_serializer(
                name="NotificationNotFoundResponse",
                fields={
                    "detail": serializers.CharField(help_text="Error message"),
                },
            ),
        },
    )
    @action(detail=True, methods=["patch"])
    def mark_as_read(self, request, pk=None):
        """
        Mark a notification as read

        Marks a notification as read for the current user.

        **Response:**
        - 200: Notification marked as read
        - 404: Notification not found
        """
        updated_count = Notification.objects.filter(
            id=pk, user=request.user
        ).update(is_read=True)

        if updated_count == 0:
            return Response(
                {"detail": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"message": "Notification marked as read", "is_read": True}
        )

    @extend_schema(
        responses={
            200: inline_serializer(
                name="AllNotificationsMarkedAsReadResponse",
                fields={
                    "message": serializers.CharField(
                        help_text="Success message with count"
                    ),
                },
            ),
        },
    )
    @action(detail=False, methods=["patch"])
    def mark_all_as_read(self, request):
        """
        Mark all notifications as read for the current user

        Marks all notifications as read for the current user.

        **Response:**
        - 200: All notifications marked as read
        """
        updated_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)

        return Response(
            {"message": f"{updated_count} notifications marked as read"}
        )
