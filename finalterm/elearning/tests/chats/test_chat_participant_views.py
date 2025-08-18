from rest_framework import status
from elearning.models import User, ChatParticipant
from elearning.tests.test_base import BaseAPITestCase


class ChatParticipantViewsTestCase(BaseAPITestCase):
    def setUp(self):
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
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Group Chat",
                "chat_type": "group",
                "participants": [self.student.id],
            },
        )
        self.chat_room_id = response.data["id"]
        self.client.force_authenticate(user=None)  # Reset authentication

    def test_create_chat_participant(self):
        """Test adding a new participant to an existing chat room"""
        self.client.force_authenticate(user=self.teacher)

        # Add another participant to the existing chat room
        participant_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"user": self.student2.id, "role": "participant"},
        )
        self.assertStatusCode(participant_response, status.HTTP_201_CREATED)

        # Verify participant was added
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(
            participants.count(), 3
        )  # teacher + student + student2

        # Check new participant
        new_participant = participants.get(user=self.student2)
        self.assertEqual(new_participant.role, "participant")
        self.assertTrue(new_participant.is_active)

    def test_update_participant_role(self):
        """Test updating a participant's role in a chat room"""
        self.client.force_authenticate(user=self.teacher)

        # Update student's role to admin
        update_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/update_role/",
            {"user": self.student.id, "role": "admin"},
        )
        self.assertStatusCode(update_response, status.HTTP_200_OK)

        # Verify role was updated
        updated_participant = ChatParticipant.objects.get(
            chat_room_id=self.chat_room_id, user=self.student
        )
        self.assertEqual(updated_participant.role, "admin")

    def test_deactivate_participant(self):
        """Test deactivating a participant in a direct chat"""
        self.client.force_authenticate(user=self.teacher)

        # Create a direct chat for this specific test
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Direct Chat",
                "chat_type": "direct",
                "participants": [self.student.id],
            },
        )

        self.assertStatusCode(response, status.HTTP_201_CREATED)
        direct_chat_id = response.data["id"]

        # Deactivate the student participant
        deactivate_response = self.client.post(
            f"/api/chats/{direct_chat_id}/participants/deactivate/",
        )
        self.assertStatusCode(deactivate_response, status.HTTP_200_OK)

        # Verify participant was deactivated
        deactivated_participant = ChatParticipant.objects.get(
            chat_room_id=direct_chat_id, user=self.teacher
        )
        self.assertFalse(deactivated_participant.is_active)

    def test_reactivate_participant(self):
        """Test reactivating a deactivated participant"""
        self.client.force_authenticate(user=self.teacher)

        # Create a direct chat for this specific test
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Direct Chat",
                "chat_type": "direct",
                "participants": [self.student.id],
            },
        )
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        direct_chat_id = response.data["id"]

        # Deactivate first
        self.client.post(
            f"/api/chats/{direct_chat_id}/participants/deactivate/",
        )

        # Reactivate
        reactivate_response = self.client.post(
            f"/api/chats/{direct_chat_id}/participants/reactivate/",
        )
        self.assertStatusCode(reactivate_response, status.HTTP_200_OK)

        # Verify participant was reactivated
        reactivated_participant = ChatParticipant.objects.get(
            chat_room_id=direct_chat_id, user=self.teacher
        )
        self.assertTrue(reactivated_participant.is_active)

    def test_participant_permissions(self):
        """Test that only chat room admins can modify participants"""
        # Try to update role as student (should fail)
        self.client.force_authenticate(user=self.student)
        update_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/update_role/",
            {"user": self.student2.id, "role": "admin"},
        )
        self.assertStatusCode(update_response, status.HTTP_403_FORBIDDEN)

    def test_participant_endpoint_validation(self):
        """Test validation of participant endpoint inputs"""
        self.client.force_authenticate(user=self.teacher)

        # Test missing user_id
        create_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"role": "participant"},
        )
        self.assertStatusCode(create_response, status.HTTP_400_BAD_REQUEST)

        # Test invalid role
        update_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/update_role/",
            {"user": self.student.id, "role": "invalid_role"},
        )
        self.assertStatusCode(update_response, status.HTTP_400_BAD_REQUEST)

    def test_list_chat_participants(self):
        """Test listing all participants in a chat room"""
        self.client.force_authenticate(user=self.teacher)

        # Get participants from the base chat room
        participant_response = self.client.get(
            f"/api/chats/{self.chat_room_id}/participants/"
        )
        self.assertStatusCode(participant_response, status.HTTP_200_OK)

        # Verify participant data structure
        participants = participant_response.data
        self.assertEqual(len(participants), 2)  # teacher + student

        # Check that user data is included
        for participant in participants:
            self.assertIn("user", participant)
            self.assertIn("role", participant)
            self.assertIn("is_active", participant)
            self.assertIn("joined_at", participant)

            # Check user object structure
            user_data = participant["user"]
            self.assertIn("id", user_data)
            self.assertIn("username", user_data)
            self.assertIn("email", user_data)
            self.assertIn("role", user_data)
