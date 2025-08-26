from rest_framework import status
from elearning.models import User, ChatParticipant
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure


class ChatParticipantViewsTestCase(BaseAPITestCase):
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
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Group Chat",
                "chat_type": "group",
                "description": "Test chat for participants",
                "is_public": True,
            },
        )
        self.chat_room_id = response.data["id"]

        self.client.force_authenticate(user=None)  # Reset authentication

    @debug_on_failure
    def test_create_chat_participant(self):
        """Test adding a new participant to an existing chat room"""
        self.client.force_authenticate(user=self.teacher)

        # Initially, only the teacher should be a participant (as admin)
        initial_participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(initial_participants.count(), 1)  # Only teacher
        self.assertEqual(initial_participants.first().user, self.teacher)
        self.assertEqual(initial_participants.first().role, "admin")

        # Add another participant to the existing chat room using username
        participant_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": self.student2.username},
        )

        # Log the response for debugging
        self.log_response(participant_response)
        self.assertStatusCode(participant_response, status.HTTP_201_CREATED)

        # Verify participant was added
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(
            participants.count(), 2
        )  # teacher (admin) + student2 (participant)

        # Check new participant
        new_participant = participants.get(user=self.student2)
        self.assertEqual(new_participant.role, "participant")
        self.assertTrue(new_participant.is_active)

    @debug_on_failure
    def test_update_participant_role(self):
        """Test updating a participant's role in a chat room"""
        self.client.force_authenticate(user=self.teacher)

        # First, add the student as a participant
        add_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": self.student.username},
        )
        self.assertStatusCode(add_response, status.HTTP_201_CREATED)

        # Update student's role to admin
        update_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/update_role/",
            {"user": self.student.id, "role": "admin"},
        )
        self.log_response(update_response)
        self.assertStatusCode(update_response, status.HTTP_200_OK)

        # Verify role was updated
        updated_participant = ChatParticipant.objects.get(
            chat_room_id=self.chat_room_id, user=self.student
        )
        self.assertEqual(updated_participant.role, "admin")

    @debug_on_failure
    def test_student_joins_public_chat(self):
        """Test that a student can join a public chat themselves"""
        self.client.force_authenticate(user=self.student)

        # Student joins the public chat
        join_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {},  # No username means join yourself
        )
        self.log_response(join_response)
        self.assertStatusCode(join_response, status.HTTP_201_CREATED)

        # Verify student was added as a participant
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(participants.count(), 2)  # teacher + student

        student_participant = participants.get(user=self.student)
        self.assertEqual(student_participant.role, "participant")
        self.assertTrue(student_participant.is_active)

    @debug_on_failure
    def test_deactivate_participant(self):
        """Test deactivating a participant in a direct chat"""
        self.client.force_authenticate(user=self.teacher)

        # Create a direct chat for this specific test
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Direct Chat",
                "chat_type": "direct",
                "description": "Test direct chat",
                "is_public": False,
                "participants": [self.student.id],
            },
        )

        self.log_response(response)
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        direct_chat_id = response.data["id"]

        # Switch to student user to deactivate themselves
        self.client.force_authenticate(user=self.student)

        # Deactivate the student participant (student deactivates themselves)
        deactivate_response = self.client.post(
            f"/api/chats/{direct_chat_id}/participants/deactivate/",
        )
        self.log_response(deactivate_response)
        self.assertStatusCode(deactivate_response, status.HTTP_200_OK)

        # Verify participant was deactivated
        deactivated_participant = ChatParticipant.objects.get(
            chat_room_id=direct_chat_id, user=self.student
        )
        self.assertFalse(deactivated_participant.is_active)

    @debug_on_failure
    def test_reactivate_participant(self):
        """Test reactivating a deactivated participant"""
        self.client.force_authenticate(user=self.teacher)

        # Create a direct chat for this specific test
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Direct Chat Reactivate",
                "chat_type": "direct",
                "description": "Test direct chat for reactivation",
                "is_public": False,
                "participants": [self.student.id],
            },
        )

        self.log_response(response)
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        direct_chat_id = response.data["id"]

        # Switch to student user for deactivate/reactivate operations
        self.client.force_authenticate(user=self.student)

        # Deactivate first (student deactivates themselves)
        deactivate_response = self.client.post(
            f"/api/chats/{direct_chat_id}/participants/deactivate/",
        )
        self.log_response(deactivate_response)
        self.assertStatusCode(deactivate_response, status.HTTP_200_OK)

        # Then reactivate
        reactivate_response = self.client.post(
            f"/api/chats/{direct_chat_id}/participants/reactivate/",
        )
        self.log_response(reactivate_response)
        self.assertStatusCode(reactivate_response, status.HTTP_200_OK)

        # Verify participant was reactivated
        reactivated_participant = ChatParticipant.objects.get(
            chat_room_id=direct_chat_id, user=self.student
        )
        self.assertTrue(reactivated_participant.is_active)

    @debug_on_failure
    def test_participant_endpoint_validation(self):
        """Test validation of participant endpoint inputs"""
        self.client.force_authenticate(user=self.teacher)

        # Test with invalid username
        create_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": "nonexistent_user"},
        )
        self.log_response(create_response)
        self.assertStatusCode(create_response, status.HTTP_404_NOT_FOUND)

        # Test with missing username field (should join the user themselves)
        create_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {},
        )
        self.log_response(create_response)
        self.assertStatusCode(create_response, status.HTTP_201_CREATED)

    @debug_on_failure
    def test_participant_permissions(self):
        """Test that only admins can add participants"""
        # Test with non-admin user
        self.client.force_authenticate(user=self.student)
        create_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": self.student2.username},
        )
        self.log_response(create_response)
        self.assertStatusCode(create_response, status.HTTP_403_FORBIDDEN)

        # Test with unauthenticated user
        self.client.force_authenticate(user=None)
        create_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": self.student2.username},
        )
        self.log_response(create_response)
        self.assertStatusCode(create_response, status.HTTP_403_FORBIDDEN)
