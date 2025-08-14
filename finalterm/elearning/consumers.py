from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        self.chat_group_name = f"chat_{self.chat_room_id}"

        # Join chat room group
        await self.channel_layer.group_add(
            self.chat_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave chat room group
        await self.channel_layer.group_discard(
            self.chat_group_name, self.channel_name
        )

    async def chat_message(self, event):
        """Generic handler for all message types"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": event["event_type"],
                    "message": event["message"],
                }
            )
        )
