from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Each user gets their own notification room.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Get user from scope (should be authenticated)
        if self.scope["user"].is_authenticated:
            # Join user's personal notification room
            self.user_id = self.scope["user"].id
            self.room_group_name = f"notifications_{self.user_id}"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send connection confirmation
            await self.send(text_data=json.dumps({
                "type": "connection.established",
                "message": "Connected to notifications",
                "user_id": self.user_id
            }))
        else:
            # Reject connection for unauthenticated users
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def notification_message(self, event):
        """
        Handle notification messages sent to the group.
        This method is called when a notification is created.
        """
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            "type": "notification",
            "notification": event["message"]
        }))
    
    async def receive(self, text_data):
        """
        Handle messages received from WebSocket.
        Currently not needed for notifications, but can be used for:
        - Mark as read confirmations
        - User preferences
        - Heartbeat/ping
        """
        try:
            data = json.loads(text_data)
            message_type = data.get("type")
            
            if message_type == "ping":
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }))
            
            elif message_type == "mark_read":
                # Handle mark as read confirmation
                notification_id = data.get("notification_id")
                if notification_id:
                    await self.send(text_data=json.dumps({
                        "type": "mark_read_confirmed",
                        "notification_id": notification_id
                    }))
                    
        except json.JSONDecodeError:
            # Invalid JSON received
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON format"
            }))
        except Exception as e:
            # Other errors
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))
