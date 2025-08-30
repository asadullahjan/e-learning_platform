from unittest.mock import patch
from elearning.models import ChatParticipant, ChatRoom, User
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure
from rest_framework import status


@patch(
    "elearning.services.chats.chat_websocket_service.ChatWebSocketService.broadcast_message"
)
class ChatMessageViewsTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass",
            role="student",
        )
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@example.com",
            password="testpass",
            role="teacher",
        )

        self.chat_room = ChatRoom.objects.create(
            name="Test Chat Room",
            created_by=self.user,
            chat_type="group",
            is_public=True,
        )
        ChatParticipant.objects.create(
            user=self.user, chat_room=self.chat_room
        )
        ChatParticipant.objects.create(
            user=self.teacher, chat_room=self.chat_room
        )

    @debug_on_failure
    def test_create_and_list_messages(self, mock_broadcast):
        """User can create a message and see it in list"""
        self.client.force_authenticate(user=self.user)
        create = self.client.post(
            f"/api/chats/{self.chat_room.id}/messages/",
            {"content": "Hello world"},
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data["content"], "Hello world")

        list_resp = self.client.get(
            f"/api/chats/{self.chat_room.id}/messages/"
        )
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(list_resp.data["count"], 1)
        self.assertEqual(
            list_resp.data["results"][0]["content"], "Hello world"
        )

    @debug_on_failure
    def test_user_cannot_edit_others_message(self, mock_broadcast):
        """Only the author can edit their own message"""
        self.client.force_authenticate(user=self.user)
        msg = self.client.post(
            f"/api/chats/{self.chat_room.id}/messages/",
            {"content": "Original"},
        ).data

        self.client.force_authenticate(user=self.teacher)
        resp = self.client.patch(
            f"/api/chats/{self.chat_room.id}/messages/{msg['id']}/",
            {"content": "Hacked"},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_private_chat_blocks_non_participants(self, mock_broadcast):
        """Non-participants cannot read private chat messages"""
        private_chat = ChatRoom.objects.create(
            name="Private Chat",
            created_by=self.user,
            chat_type="group",
            is_public=False,
        )
        ChatParticipant.objects.create(user=self.user, chat_room=private_chat)

        self.client.force_authenticate(user=self.user)
        self.client.post(
            f"/api/chats/{private_chat.id}/messages/",
            {"content": "Private msg"},
        )

        self.client.force_authenticate(user=self.teacher)
        resp = self.client.get(f"/api/chats/{private_chat.id}/messages/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_public_chat_allows_unauthenticated_read(self, mock_broadcast):
        """Anyone can read messages in public chats"""
        self.client.force_authenticate(user=self.user)
        self.client.post(
            f"/api/chats/{self.chat_room.id}/messages/",
            {"content": "Public msg"},
        )

        self.client.force_authenticate(user=None)
        resp = self.client.get(f"/api/chats/{self.chat_room.id}/messages/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"][0]["content"], "Public msg")
