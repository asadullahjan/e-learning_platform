from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class ChatWebSocketService:
    @staticmethod
    def broadcast_message(message, event_type):
        """Broadcast message to all users in the chat room"""
        channel_layer = get_channel_layer()
        chat_group_name = f"chat_{message['chat_room']}"

        async_to_sync(channel_layer.group_send)(
            chat_group_name,
            {
                "type": "chat_message",
                "event_type": event_type,
                "message": message,
            },
        )
