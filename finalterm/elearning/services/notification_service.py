from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from elearning.models import Notification


class NotificationService:
    """Service for creating notifications and sending WebSocket messages"""

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
