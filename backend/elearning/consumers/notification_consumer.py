from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Each user gets their own notification room.
    """

    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Get user from scope (should be authenticated via
            # AuthMiddlewareStack)
            user = self.scope.get("user")

            if not user or not user.is_authenticated:
                # Reject connection for unauthenticated users
                await self.close(code=4001)  # Custom code for auth failure
                return

            # Join user's personal notification room
            self.user_id = user.id
            self.room_group_name = f"notifications_{self.user_id}"

            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )

            await self.accept()

            # Send connection confirmation
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "connection.established",
                        "message": "Connected to notifications",
                        "user_id": self.user_id,
                    }
                )
            )

        except Exception as e:
            # Log the error and close connection
            print(f"WebSocket connection error: {e}")
            await self.close(code=4000)  # Custom code for general error

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def notification_message(self, event):
        """
        Handle notification messages sent to the group.
        This method is called when a notification is created.
        """
        # Send notification to WebSocket
        await self.send(
            text_data=json.dumps(
                {"type": "notification", "notification": event["message"]}
            )
        )
