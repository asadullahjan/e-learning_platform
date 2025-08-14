from django.test import TestCase
from channels.testing import WebsocketCommunicator
from asgiref.sync import async_to_sync
from elearning.models import ChatRoom, User, ChatParticipant
from elearning_project.asgi import test_application


class WebSocketIntegrationTest(TestCase):
    def setUp(self):
        super().setUp()
        # Create test data
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass",
            role="student",
        )
        self.chat_room = ChatRoom.objects.create(
            name="Test Chat Room",
            created_by=self.user,
            chat_type="group",
        )
        ChatParticipant.objects.create(
            user=self.user,
            chat_room=self.chat_room,
        )

    @async_to_sync
    async def test_websocket_connection(self):
        """Test basic WebSocket connection"""

        communicator = WebsocketCommunicator(
            test_application, f"/ws/chat/{self.chat_room.id}/"
        )

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Clean up
        await communicator.disconnect()

    @async_to_sync
    async def test_multiple_connections(self):
        """Test multiple clients can connect to the same chat room"""

        # Connect first client
        client1 = WebsocketCommunicator(
            test_application, f"/ws/chat/{self.chat_room.id}/"
        )

        # Connect second client
        client2 = WebsocketCommunicator(
            test_application, f"/ws/chat/{self.chat_room.id}/"
        )

        try:
            connected1, _ = await client1.connect()
            connected2, _ = await client2.connect()

            self.assertTrue(connected1)
            self.assertTrue(connected2)

        finally:
            await client1.disconnect()
            await client2.disconnect()
