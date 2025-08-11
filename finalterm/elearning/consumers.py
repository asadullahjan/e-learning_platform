from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """User connects to WebSocket"""
        # Accept the connection
        await self.accept()
        print("WebSocket connected!")  # Debug message

    async def disconnect(self, close_code):
        """User disconnects from WebSocket"""
        print(f"WebSocket disconnected! Code: {close_code}")  # Debug message

    async def receive(self, text_data):
        """User sends message via WebSocket"""
        print(f"Received message: {text_data}")  # Debug message
        # For now, just echo back
        await self.send(
            text_data=json.dumps({"message": f"Echo: {text_data}"})
        )
