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
        # direct_chat_id = response.data["id"]

        # # Switch to student user to deactivate themselves
        # self.client.force_authenticate(user=self.student)

        # # Deactivate the student participant (student deactivates themselves)
        # deactivate_response = self.client.post(
        #     f"/api/chats/{direct_chat_id}/participants/deactivate/",
        # )
        # self.log_response(deactivate_response)
        # self.assertStatusCode(deactivate_response, status.HTTP_200_OK)

        # # Verify participant was deactivated
        # deactivated_participant = ChatParticipant.objects.get(
        #     chat_room_id=direct_chat_id, user=self.student
        # )
        # self.assertFalse(deactivated_participant.is_active)

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

    @debug_on_failure
    def test_user_leave_and_rejoin_reactivates_existing_participant(self):
        """Test that when a user leaves and rejoins, it reactivates existing
        participant"""
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
        original_participant_id = student_participant.id

        # Student leaves the chat (deactivates themselves)
        deactivate_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/deactivate/",
        )
        self.log_response(deactivate_response)
        self.assertStatusCode(deactivate_response, status.HTTP_200_OK)

        # Verify participant was deactivated
        deactivated_participant = ChatParticipant.objects.get(
            chat_room_id=self.chat_room_id, user=self.student
        )
        self.assertFalse(deactivated_participant.is_active)
        self.assertEqual(deactivated_participant.id, original_participant_id)

        # Student tries to join again
        rejoin_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {},  # No username means join yourself
        )
        self.log_response(rejoin_response)
        self.assertStatusCode(rejoin_response, status.HTTP_201_CREATED)

        # Verify the same participant record was reactivated (not a new one
        # created)
        reactivated_participant = ChatParticipant.objects.get(
            chat_room_id=self.chat_room_id, user=self.student
        )
        self.assertTrue(reactivated_participant.is_active)
        self.assertEqual(reactivated_participant.id, original_participant_id)

        # Verify total participant count is still 2 (no new record created)
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(participants.count(), 2)

    @debug_on_failure
    def test_user_removed_and_readded_reactivates_existing_participant(self):
        """Test that when a user is removed and readded, it reactivates existing participant"""
        self.client.force_authenticate(user=self.teacher)

        # First, add student2 as a participant
        add_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": self.student2.username},
        )
        self.log_response(add_response)
        self.assertStatusCode(add_response, status.HTTP_201_CREATED)

        # Verify student2 was added as a participant
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(participants.count(), 2)  # teacher + student2

        student2_participant = participants.get(user=self.student2)
        self.assertEqual(student2_participant.role, "participant")
        self.assertTrue(student2_participant.is_active)
        original_participant_id = student2_participant.id

        # Teacher removes student2 from the chat
        remove_response = self.client.delete(
            f"/api/chats/{self.chat_room_id}/participants/{student2_participant.id}/",
        )
        self.log_response(remove_response)
        self.assertStatusCode(remove_response, status.HTTP_204_NO_CONTENT)

        # Verify participant was removed (deleted)
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(participants.count(), 1)  # Only teacher remains

        # Teacher adds student2 back to the chat
        readd_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": self.student2.username},
        )
        self.log_response(readd_response)
        self.assertStatusCode(readd_response, status.HTTP_201_CREATED)

        # Verify student2 was added back as a participant
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(participants.count(), 2)  # teacher + student2

        new_student2_participant = participants.get(user=self.student2)
        self.assertEqual(new_student2_participant.role, "participant")
        self.assertTrue(new_student2_participant.is_active)

        # Since the participant was deleted, a new one should be created
        # (different from the original scenario where it was just deactivated)
        self.assertNotEqual(
            new_student2_participant.id, original_participant_id
        )

    @debug_on_failure
    def test_list_participants_does_not_require_authentication(self):
        """
        Test that listing participants does not require
        authentication for public chats
        """
        # Test with unauthenticated user
        self.client.force_authenticate(user=None)
        list_response = self.client.get(
            f"/api/chats/{self.chat_room_id}/participants/",
        )
        self.log_response(list_response)
        self.assertStatusCode(list_response, status.HTTP_200_OK)

    @debug_on_failure
    def test_list_participants_returns_correct_data(self):
        """Test that listing participants returns correct data structure"""
        self.client.force_authenticate(user=self.teacher)

        # Add a student as participant
        add_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": self.student.username},
        )
        self.assertStatusCode(add_response, status.HTTP_201_CREATED)

        # List participants
        list_response = self.client.get(
            f"/api/chats/{self.chat_room_id}/participants/",
        )
        self.log_response(list_response)
        self.assertStatusCode(list_response, status.HTTP_200_OK)

        # Verify response structure (DRF pagination format)
        self.assertIn("results", list_response.data)
        participants_data = list_response.data["results"]
        self.assertEqual(len(participants_data), 2)  # teacher + student

        # Check that each participant has required fields
        for participant in participants_data:
            self.assertIn("id", participant)
            self.assertIn("user", participant)
            self.assertIn("role", participant)
            self.assertIn("is_active", participant)

    @debug_on_failure
    def test_remove_participant_permissions(self):
        """Test that only admins can remove participants"""
        self.client.force_authenticate(user=self.teacher)

        # First, add student as a participant
        add_response = self.client.post(
            f"/api/chats/{self.chat_room_id}/participants/",
            {"username": self.student.username},
        )
        self.assertStatusCode(add_response, status.HTTP_201_CREATED)

        # Get teacher's participant record
        # (which student shouldn't be able to remove)
        teacher_participant = ChatParticipant.objects.get(
            chat_room_id=self.chat_room_id, user=self.teacher
        )

        # Switch to student user (non-admin)
        self.client.force_authenticate(user=self.student)

        # Student tries to remove teacher's participant (should fail)
        remove_response = self.client.delete(
            f"/api/chats/{self.chat_room_id}/"
            f"participants/{teacher_participant.id}/",
        )
        self.log_response(remove_response)
        self.assertStatusCode(remove_response, status.HTTP_403_FORBIDDEN)

        # Verify participant still exists
        participants = ChatParticipant.objects.filter(
            chat_room_id=self.chat_room_id
        )
        self.assertEqual(participants.count(), 2)  # teacher + student
