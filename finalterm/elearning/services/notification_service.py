from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from elearning.models import Notification, User
from elearning.exceptions import ServiceError
from elearning.permissions.users.notification_permissions import (
    NotificationPolicy
)


class NotificationService:
    """Service for notification operations with policy-based gatekeeping"""

    @staticmethod
    def create_notifications_and_send(
        user_ids: list[int], title: str, message: str, action_url: str
    ) -> list[Notification]:
        """
        Create notifications for users and send WebSocket messages.
        Works for both single user (list with one ID) and multiple users.

        Args:
            user_ids: List of user IDs to notify (can be single ID in list)
            title: Notification title
            message: Notification message
            action_url: URL to navigate to when clicked

        Returns:
            List of created notification objects
        """
        notifications = []

        for user_id in user_ids:
            notification = Notification.objects.create(
                user_id=user_id,
                title=title,
                message=message,
                action_url=action_url,
            )
            notifications.append(notification)

        # Send WebSocket messages to all users
        for notification in notifications:
            NotificationService._send_websocket_message(notification)

        return notifications

    @staticmethod
    def _send_websocket_message(notification: Notification):
        """Send WebSocket message to the notification recipient"""
        channel_layer = get_channel_layer()

        # Send to user's personal notification room
        async_to_sync(channel_layer.group_send)(
            f"notifications_{notification.user.id}",
            {
                "type": "notification.message",
                "message": {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "action_url": notification.action_url,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                },
            },
        )

    @staticmethod
    def get_notification_with_permission_check(
        notification_id: int, user: User
    ) -> Notification:
        """Get notification with permission check using policy"""
        try:
            notification = Notification.objects.get(id=notification_id)
            # Use policy for gatekeeping
            NotificationPolicy.check_can_view_notification(
                user, notification, raise_exception=True
            )
            return notification
        except Notification.DoesNotExist:
            raise ServiceError.not_found("Notification not found")

    @staticmethod
    def mark_notification_read(
        notification: Notification, user: User
    ) -> Notification:
        """Mark notification as read with policy-based gatekeeping"""
        # Use policy for gatekeeping
        NotificationPolicy.check_can_mark_notification_read(
            user, notification, raise_exception=True
        )

        notification.is_read = True
        notification.save()
        return notification

    @staticmethod
    def mark_all_notifications_read(user: User) -> int:
        """Mark all notifications as read for a user"""
        # Simple operation - no complex gatekeeping needed
        updated_count = Notification.objects.filter(
            user=user, is_read=False
        ).update(is_read=True)
        return updated_count

    @staticmethod
    def delete_notification(notification: Notification, user: User):
        """Delete notification with policy-based gatekeeping"""
        # Use policy for gatekeeping
        NotificationPolicy.check_can_delete_notification(
            user, notification, raise_exception=True
        )
        
        notification.delete()

    @staticmethod
    def get_user_notifications(user: User):
        """Get all notifications for a user"""
        return Notification.objects.filter(user=user).order_by("-created_at")
