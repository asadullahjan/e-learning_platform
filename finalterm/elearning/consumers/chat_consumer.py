from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.core.exceptions import ObjectDoesNotExist

from elearning.models import ChatRoom
from elearning.permissions.chats.chat_room_permissions import ChatPolicy


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        self.chat_group_name = f"chat_{self.chat_room_id}"
        user = self.scope["user"]

        # Fetch chat room safely
        try:
            chat_room = await self.get_chat_room(self.chat_room_id)
        except ObjectDoesNotExist:
            await self.close(code=4004)
            return

        # Check access policy
        allowed = await self.can_access_chat(user, chat_room)
        if not allowed:
            await self.close(code=4003)
            return

        # Join chat room group
        await self.channel_layer.group_add(
            self.chat_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name, self.channel_name
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": event["event_type"],
                    "message": event["message"],
                }
            )
        )

    # --- Async DB wrappers ---
    @database_sync_to_async
    def get_chat_room(self, chat_room_id):
        return ChatRoom.objects.get(id=chat_room_id)

    @database_sync_to_async
    def can_access_chat(self, user, chat_room):
        return ChatPolicy.check_can_access_chat_room(user, chat_room)
