from elearning.models import ChatParticipant, ChatRoom, User
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure
from rest_framework.test import APIClient
from rest_framework import status


class ChatMessageViewsTestCase(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
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

        self.client.force_authenticate(user=self.user)
        self.chat_room = ChatRoom.objects.create(
            name="Test Chat Room",
            created_by=self.user,
            chat_type="group",
        )
        ChatParticipant.objects.create(
            user=self.user,
            chat_room=self.chat_room,
        )
        ChatParticipant.objects.create(
            user=self.teacher,
            chat_room=self.chat_room,
        )

        self.client.force_authenticate(user=None)

    @debug_on_failure
    def test_create_message(self):
        self.client.force_authenticate(user=self.user)
        response = self.log_response(
            self.client.post(
                f"/api/chats/{self.chat_room.id}/messages/",
                {"content": "Test message"},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "Test message")

    @debug_on_failure
    def test_list_messages(self):
        self.client.force_authenticate(user=self.user)
        response = self.log_response(
            self.client.post(
                f"/api/chats/{self.chat_room.id}/messages/",
                {"content": "Test message"},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "Test message")

        response = self.log_response(
            self.client.get(f"/api/chats/{self.chat_room.id}/messages/")
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["content"], "Test message"
        )

    @debug_on_failure
    def test_update_message(self):
        self.client.force_authenticate(user=self.user)
        response = self.log_response(
            self.client.post(
                f"/api/chats/{self.chat_room.id}/messages/",
                {"content": "Test message"},
            )
        )
        self.assertIn("id", response.data)
        message_id = response.data["id"]
        response = self.log_response(
            self.client.patch(
                f"/api/chats/{self.chat_room.id}/messages/{message_id}/",
                {"content": "Updated message"},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Updated message")

    @debug_on_failure
    def test_update_another_users_message(self):
        self.client.force_authenticate(user=self.user)
        response = self.log_response(
            self.client.post(
                f"/api/chats/{self.chat_room.id}/messages/",
                {"content": "Test message"},
            )
        )
        self.assertIn("id", response.data)
        message_id = response.data["id"]
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.patch(
                f"/api/chats/{self.chat_room.id}/messages/{message_id}/",
                {"content": "Updated message"},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"], "You are not the sender of this message"
        )

    @debug_on_failure
    def test_delete_message(self):
        self.client.force_authenticate(user=self.user)
        response = self.log_response(
            self.client.post(
                f"/api/chats/{self.chat_room.id}/messages/",
                {"content": "Test message"},
            )
        )
        self.assertIn("id", response.data)
        message_id = response.data["id"]
        response = self.log_response(
            self.client.delete(
                f"/api/chats/{self.chat_room.id}/messages/{message_id}/"
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
