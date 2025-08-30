from channels.testing import WebsocketCommunicator
from asgiref.sync import async_to_sync
from elearning.models import ChatRoom, User, ChatParticipant
from elearning_project.asgi import test_application
from elearning.tests.test_base import BaseTestCase, debug_on_failure


class ChatWebSocketTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.participant = User.objects.create_user(
            username="participant",
            email="participant@example.com",
            password="testpass",
            role="student",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="testpass",
            role="student",
        )

        # Public chat
        self.public_chat = ChatRoom.objects.create(
            name="Public Chat",
            created_by=self.participant,
            chat_type="group",
            is_public=True,
        )
        ChatParticipant.objects.create(
            user=self.participant, chat_room=self.public_chat
        )

        # Private chat
        self.private_chat = ChatRoom.objects.create(
            name="Private Chat",
            created_by=self.participant,
            chat_type="group",
            is_public=False,
        )
        ChatParticipant.objects.create(
            user=self.participant, chat_room=self.private_chat
        )

    @debug_on_failure
    @async_to_sync
    async def test_public_chat_access(self):
        """Both participant and non-participant can join public chat"""
        # participant
        comm1 = WebsocketCommunicator(
            test_application, f"/ws/chat/{self.public_chat.id}/"
        )
        comm1.scope["user"] = self.participant
        connected1, _ = await comm1.connect()
        self.assertTrue(connected1)
        await comm1.disconnect()

        # non-participant
        comm2 = WebsocketCommunicator(
            test_application, f"/ws/chat/{self.public_chat.id}/"
        )
        comm2.scope["user"] = self.other_user
        connected2, _ = await comm2.connect()
        self.assertTrue(connected2)  # allowed in public chat
        await comm2.disconnect()

    @debug_on_failure
    @async_to_sync
    async def test_private_chat_access(self):
        """Only participants can join private chat"""
        # participant
        comm1 = WebsocketCommunicator(
            test_application, f"/ws/chat/{self.private_chat.id}/"
        )
        comm1.scope["user"] = self.participant
        connected1, _ = await comm1.connect()
        self.assertTrue(connected1)
        await comm1.disconnect()

        # non-participant
        comm2 = WebsocketCommunicator(
            test_application, f"/ws/chat/{self.private_chat.id}/"
        )
        comm2.scope["user"] = self.other_user
        connected2, _ = await comm2.connect()
        self.assertFalse(connected2)  # should be rejected (4003)
        await comm2.disconnect()
