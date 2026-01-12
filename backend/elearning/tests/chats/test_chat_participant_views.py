from rest_framework import status
from elearning.models import User, ChatParticipant
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure


class ChatParticipantViewsTestCase(BaseAPITestCase):
    @debug_on_failure
    def setUp(self):
        super().setUp()
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@example.com",
            password="password",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="password",
            role="student",
        )
        self.student2 = User.objects.create_user(
            username="student2",
            email="student2@example.com",
            password="password",
            role="student",
        )

        # Create a base group chat for participant tests
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Test Group Chat",
                    "chat_type": "group",
                    "description": "Test chat for participants",
                    "is_public": True,
                },
            )
        )
        self.chat_room_id = response.data["id"]
        self.client.force_authenticate(user=None)  # Reset authentication

    def _add_participant(
        self,
        user,
        acting_user=None,
        payload=None,
        expected_status=status.HTTP_201_CREATED,
    ):
        """Helper for adding a participant via API."""
        if acting_user:
            self.client.force_authenticate(user=acting_user)
        response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            payload or {"user": user.id} if user else {},
        )
        self.log_response(response)
        self.assertStatusCode(response, expected_status)
        return response

    @debug_on_failure
    def test_join_chat(self):
        """Test that participants can be added by admin or by themselves in a public chat"""
        # Teacher (admin) adds student2
        self._add_participant(self.student2, acting_user=self.teacher)

        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(participants.count(), 2)  # teacher + student2
        self.assertTrue(participants.get(user=self.student2).is_active)

        # Student joins by themselves
        self._add_participant(
            None, acting_user=self.student
        )  # empty payload → join self
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(
            participants.count(), 3
        )  # teacher + student2 + student
        self.assertTrue(participants.get(user=self.student).is_active)

    @debug_on_failure
    def test_update_participant_role(self):
        """Test updating a participant's role in a chat room"""
        self._add_participant(self.student, acting_user=self.teacher)
        update_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/update_role/",
            {"user": self.student.id, "role": "admin"},
        )
        self.log_response(update_response)
        self.assertStatusCode(update_response, status.HTTP_200_OK)
        self.assertEqual(
            ChatParticipant.objects.get(
                chat_room_id=self.chat_room_id, user=self.student
            ).role,
            "admin",
        )

    @debug_on_failure
    def test_deactivate_and_reactivate_participant(self):
        """Test deactivating and reactivating a participant"""
        self._add_participant(
            None, acting_user=self.student
        )  # student joins self
        participant = ChatParticipant.objects.get(
            chat_room_id=self.chat_room_id, user=self.student
        )
        original_id = participant.id

        # Deactivate
        deactivate_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/deactivate/",
        )
        self.log_response(deactivate_response)
        self.assertStatusCode(deactivate_response, status.HTTP_200_OK)
        self.assertFalse(ChatParticipant.objects.get(id=original_id).is_active)

        # Reactivate
        reactivate_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/reactivate/",
        )
        self.log_response(reactivate_response)
        self.assertStatusCode(reactivate_response, status.HTTP_200_OK)
        self.assertTrue(ChatParticipant.objects.get(id=original_id).is_active)

    @debug_on_failure
    def test_participant_endpoint_validation(self):
        """Test validation for invalid or missing user field"""
        self.client.force_authenticate(user=self.teacher)

        # Invalid id → should 400
        invalid_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"user": 9999},
        )
        self.log_response(invalid_response)
        self.assertStatusCode(invalid_response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid pk", invalid_response.data["user"][0])

        # Missing id field → should join the current user
        create_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {},
        )
        self.log_response(create_response)
        self.assertStatusCode(create_response, status.HTTP_201_CREATED)

    @debug_on_failure
    def test_participant_permissions(self):
        """Test that only admins can add participants"""
        # Non-admin cannot add others
        self._add_participant(
            self.student2,
            acting_user=self.student,
            expected_status=status.HTTP_403_FORBIDDEN,
        )

        # Unauthenticated cannot add
        self._add_participant(
            self.student2,
            acting_user=None,
            expected_status=status.HTTP_403_FORBIDDEN,
        )

    @debug_on_failure
    def test_list_participants_returns_correct_data(self):
        """Test that listing participants returns correct data structure"""
        self._add_participant(self.student, acting_user=self.teacher)

        list_response = self.client.get(
            f"/api/chats/{self.chat_room_id}/participants/"
        )
        self.log_response(list_response)
        self.assertStatusCode(list_response, status.HTTP_200_OK)

        self.assertIn("results", list_response.data)
        participants_data = list_response.data["results"]
        self.assertEqual(len(participants_data), 2)  # teacher + student

        for participant in participants_data:
            self.assertIn("id", participant)
            self.assertIn("user", participant)
            self.assertIn("role", participant)
            self.assertIn("is_active", participant)
