from unittest.mock import patch
from rest_framework import status
from elearning.models import ChatRoom, User, ChatParticipant
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure


@patch(
    "elearning.services.chats.chat_websocket_service.ChatWebSocketService.broadcast_message"
)
class ChatRoomViewsTestCase(BaseAPITestCase):
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
        self.client.force_authenticate(user=self.user)

    # --- my_chats endpoint ---
    @debug_on_failure
    def test_my_chats_only_active_and_no_pagination(self, mock_broadcast):
        chat1 = ChatRoom.objects.create(
            name="Active Chat", created_by=self.user, chat_type="group"
        )
        chat2 = ChatRoom.objects.create(
            name="Inactive Chat", created_by=self.user, chat_type="group"
        )
        ChatParticipant.objects.create(
            user=self.user, chat_room=chat1, is_active=True
        )
        ChatParticipant.objects.create(
            user=self.user, chat_room=chat2, is_active=False
        )

        response = self.log_response(self.client.get("/api/chats/my_chats/"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Active Chat")

    @debug_on_failure
    def test_my_chats_isolated_between_users_and_requires_auth(
        self, mock_broadcast
    ):
        chat = ChatRoom.objects.create(
            name="Shared Chat", created_by=self.user, chat_type="group"
        )
        ChatParticipant.objects.create(user=self.user, chat_room=chat)
        ChatParticipant.objects.create(user=self.teacher, chat_room=chat)

        # user sees only their chats
        self.client.force_authenticate(user=self.user)
        response = self.log_response(self.client.get("/api/chats/my_chats/"))
        self.assertEqual(len(response.data), 1)

        # teacher sees only their chats
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(self.client.get("/api/chats/my_chats/"))
        self.assertEqual(len(response.data), 1)

        # unauthenticated forbidden
        self.client.force_authenticate(user=None)
        response = self.log_response(self.client.get("/api/chats/my_chats/"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- chat creation ---
    @debug_on_failure
    def test_create_direct_chat_and_duplicate_prevention(self, mock_broadcast):
        payload = {
            "name": "Direct",
            "chat_type": "direct",
            "participants": [self.teacher.id],
        }
        response = self.log_response(self.client.post("/api/chats/", payload))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["chat_type"], "direct")

        # duplicate direct chat -> existing returned
        response2 = self.log_response(self.client.post("/api/chats/", payload))
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data["id"], response.data["id"])

    @debug_on_failure
    def test_create_group_chat_success(self, mock_broadcast):
        payload = {
            "name": "Study Group",
            "chat_type": "group",
            "description": "Test group chat",
            "is_public": True,
        }
        response = self.log_response(self.client.post("/api/chats/", payload))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["chat_type"], "group")
        self.assertEqual(response.data["name"], "Study Group")

    @debug_on_failure
    def test_create_chat_invalid_payloads(self, mock_broadcast):
        # short name
        response = self.client.post(
            "/api/chats/", {"name": "x", "chat_type": "group"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # invalid type
        response = self.client.post(
            "/api/chats/", {"name": "Bad", "chat_type": "invalid"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # direct chat requires exactly one participant
        response = self.client.post(
            "/api/chats/", {"name": "Invalid", "chat_type": "direct"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # nonexistent user
        response = self.client.post(
            "/api/chats/",
            {"name": "Ghost", "chat_type": "direct", "participants": [9999]},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- access control ---
    @debug_on_failure
    def test_list_and_retrieve_chats_public_vs_private(self, mock_broadcast):
        public_chat = ChatRoom.objects.create(
            name="Public Chat",
            created_by=self.user,
            chat_type="group",
            is_public=True,
        )
        private_chat = ChatRoom.objects.create(
            name="Private Chat",
            created_by=self.user,
            chat_type="group",
            is_public=False,
        )
        ChatParticipant.objects.create(user=self.user, chat_room=private_chat)

        # list all chats (public + joined)
        response = self.log_response(self.client.get("/api/chats/"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "Public Chat", [c["name"] for c in response.data["results"]]
        )
        self.assertIn(
            "Private Chat", [c["name"] for c in response.data["results"]]
        )

        # unauthenticated sees only public
        self.client.force_authenticate(user=None)
        response = self.log_response(self.client.get("/api/chats/"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "Public Chat", [c["name"] for c in response.data["results"]]
        )
        self.assertNotIn(
            "Private Chat", [c["name"] for c in response.data["results"]]
        )

        # retrieve public allowed
        response = self.client.get(f"/api/chats/{public_chat.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # retrieve private forbidden if not participant
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f"/api/chats/{private_chat.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- update & delete ---
    @debug_on_failure
    def test_only_creator_can_update_or_delete(self, mock_broadcast):
        chat = ChatRoom.objects.create(
            name="Updatable", created_by=self.user, chat_type="group"
        )

        # creator can update
        response = self.log_response(
            self.client.patch(f"/api/chats/{chat.id}/", {"name": "Renamed"})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # other user forbidden
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.patch(f"/api/chats/{chat.id}/", {"name": "Hacked"})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # creator can delete
        self.client.force_authenticate(user=self.user)
        response = self.log_response(
            self.client.delete(f"/api/chats/{chat.id}/")
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # other user forbidden
        chat2 = ChatRoom.objects.create(
            name="Protected", created_by=self.user, chat_type="group"
        )
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(f"/api/chats/{chat2.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
