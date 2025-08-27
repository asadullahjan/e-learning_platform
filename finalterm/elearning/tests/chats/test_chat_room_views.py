from rest_framework import status
from elearning.models import User, ChatRoom, ChatParticipant
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure


class ChatRoomViewsTestCase(BaseAPITestCase):
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

    @debug_on_failure
    def test_my_chats_returns_only_user_chats(self):
        """Test that my_chats returns only chats where user is an active
        participant"""
        self.client.force_authenticate(user=self.teacher)

        # Create a chat where teacher is participant
        teacher_chat = ChatRoom.objects.create(
            name="Teacher's Chat", chat_type="group", created_by=self.teacher
        )
        ChatParticipant.objects.create(
            chat_room=teacher_chat,
            user=self.teacher,
            role="admin",
            is_active=True,
        )

        # Create a chat where teacher is NOT participant
        other_chat = ChatRoom.objects.create(
            name="Other Chat", chat_type="group", created_by=self.student
        )
        ChatParticipant.objects.create(
            chat_room=other_chat,
            user=self.student,
            role="admin",
            is_active=True,
        )

        # Create a chat where teacher was participant but is now inactive
        inactive_chat = ChatRoom.objects.create(
            name="Inactive Chat", chat_type="group", created_by=self.teacher
        )
        ChatParticipant.objects.create(
            chat_room=inactive_chat,
            user=self.teacher,
            role="admin",
            is_active=False,  # Inactive!
        )

        response = self.log_response(self.client.get("/api/chats/my_chats/"))

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only active teacher chat

        # Should only return the active chat
        returned_chat = response.data[0]
        self.assertEqual(returned_chat["id"], teacher_chat.id)
        self.assertEqual(returned_chat["name"], "Teacher's Chat")

        # Should NOT return the other chat or inactive chat
        chat_ids = [chat["id"] for chat in response.data]
        self.assertNotIn(other_chat.id, chat_ids)
        self.assertNotIn(inactive_chat.id, chat_ids)

    @debug_on_failure
    def test_my_chats_no_pagination(self):
        """Test that my_chats returns all results without pagination"""
        self.client.force_authenticate(user=self.teacher)

        # Create multiple chats for the teacher
        for i in range(25):  # More than typical pagination limit
            chat = ChatRoom.objects.create(
                name=f"Teacher Chat {i}",
                chat_type="group",
                created_by=self.teacher,
            )
            ChatParticipant.objects.create(
                chat_room=chat, user=self.teacher, role="admin", is_active=True
            )

        response = self.log_response(self.client.get("/api/chats/my_chats/"))

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 25)  # All chats returned

        # Verify no pagination metadata
        self.assertNotIn("count", response.data)
        self.assertNotIn("next", response.data)
        self.assertNotIn("previous", response.data)
        self.assertNotIn("results", response.data)

    @debug_on_failure
    def test_my_chats_unauthenticated(self):
        """Test that unauthenticated users cannot access my_chats"""
        response = self.log_response(self.client.get("/api/chats/my_chats/"))
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_my_chats_empty_when_no_chats(self):
        """Test that my_chats returns empty list when user has no active
        chats"""
        self.client.force_authenticate(user=self.teacher)

        response = self.log_response(self.client.get("/api/chats/my_chats/"))

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])

    @debug_on_failure
    def test_my_chats_includes_different_chat_types(self):
        """Test that my_chats includes all chat types where user is active
        participant"""
        self.client.force_authenticate(user=self.teacher)

        # Create different types of chats
        direct_chat = ChatRoom.objects.create(
            name="Direct Chat", chat_type="direct", created_by=self.teacher
        )
        ChatParticipant.objects.create(
            chat_room=direct_chat,
            user=self.teacher,
            role="participant",
            is_active=True,
        )

        group_chat = ChatRoom.objects.create(
            name="Group Chat", chat_type="group", created_by=self.teacher
        )
        ChatParticipant.objects.create(
            chat_room=group_chat,
            user=self.teacher,
            role="admin",
            is_active=True,
        )

        course_chat = ChatRoom.objects.create(
            name="Course Chat", chat_type="course", created_by=self.teacher
        )
        ChatParticipant.objects.create(
            chat_room=course_chat,
            user=self.teacher,
            role="admin",
            is_active=True,
        )

        response = self.log_response(self.client.get("/api/chats/my_chats/"))

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # Verify all chat types are included
        chat_types = [chat["chat_type"] for chat in response.data]
        self.assertIn("direct", chat_types)
        self.assertIn("group", chat_types)
        self.assertIn("course", chat_types)

    @debug_on_failure
    def test_my_chats_respects_user_isolation(self):
        """Test that users only see their own chats, not other users'
        chats"""
        self.client.force_authenticate(user=self.teacher)

        # Create chat for teacher
        teacher_chat = ChatRoom.objects.create(
            name="Teacher's Private Chat",
            chat_type="group",
            created_by=self.teacher,
        )
        ChatParticipant.objects.create(
            chat_room=teacher_chat,
            user=self.teacher,
            role="admin",
            is_active=True,
        )

        # Create chat for student
        student_chat = ChatRoom.objects.create(
            name="Student's Private Chat",
            chat_type="group",
            created_by=self.student,
        )
        ChatParticipant.objects.create(
            chat_room=student_chat,
            user=self.student,
            role="admin",
            is_active=True,
        )

        # Teacher should only see their own chat
        response = self.log_response(self.client.get("/api/chats/my_chats/"))
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], teacher_chat.id)

        # Switch to student and verify they only see their chat
        self.client.force_authenticate(user=self.student)
        response = self.log_response(self.client.get("/api/chats/my_chats/"))
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], student_chat.id)

    @debug_on_failure
    def test_create_direct_chat_room(self):
        """Test creating a direct chat room with proper participants"""
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Test Direct Chat",
                    "chat_type": "direct",
                    "participants": [self.student.id],
                },
            )
        )

        self.assertStatusCode(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Direct Chat")
        self.assertEqual(response.data["chat_type"], "direct")
        self.assertEqual(response.data["is_public"], False)

        # Verify chat room was created in database
        chat_room = ChatRoom.objects.get(id=response.data["id"])
        self.assertEqual(chat_room.created_by, self.teacher)
        self.assertEqual(chat_room.chat_type, "direct")

        # Verify participants were added correctly
        participants = ChatParticipant.objects.filter(chat_room=chat_room)
        self.assertEqual(
            participants.count(), 2
        )  # creator + student (both participants)

        # Check creator is participant (not admin for direct chats)
        creator_participant = participants.get(user=self.teacher)
        self.assertEqual(creator_participant.role, "participant")
        self.assertTrue(creator_participant.is_active)

        # Check student is participant
        student_participant = participants.get(user=self.student)
        self.assertEqual(student_participant.role, "participant")
        self.assertTrue(student_participant.is_active)

    @debug_on_failure
    def test_create_group_chat_room(self):
        """Test creating a group chat room with multiple participants"""
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Test Group Chat",
                    "chat_type": "group",
                    "participants": [self.student.id, self.student2.id],
                },
            )
        )

        self.assertStatusCode(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Group Chat")
        self.assertEqual(response.data["chat_type"], "group")

        # Verify participants were added correctly
        chat_room = ChatRoom.objects.get(id=response.data["id"])
        participants = ChatParticipant.objects.filter(chat_room=chat_room)
        self.assertEqual(participants.count(), 3)  # creator + 2 students

        # Check creator is admin
        creator_participant = participants.get(user=self.teacher)
        self.assertEqual(creator_participant.role, "admin")

        # Check students are participants
        student_participants = participants.filter(
            user__in=[self.student, self.student2]
        )
        self.assertEqual(student_participants.count(), 2)
        for participant in student_participants:
            self.assertEqual(participant.role, "participant")

    @debug_on_failure
    def test_create_direct_chat_duplicate(self):
        """Test that creating duplicate direct chats returns existing chat"""
        self.client.force_authenticate(user=self.teacher)

        # Create first chat
        response1 = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Test Direct Chat",
                    "chat_type": "direct",
                    "participants": [self.student.id],
                },
            )
        )
        self.assertStatusCode(response1, status.HTTP_201_CREATED)
        first_chat_id = response1.data["id"]

        # Try to create duplicate chat
        response2 = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Another Direct Chat",
                    "chat_type": "direct",
                    "participants": [self.student.id],
                },
            )
        )
        self.assertStatusCode(response2, status.HTTP_201_CREATED)

        # Should return the same chat room
        self.assertEqual(response2.data["id"], first_chat_id)
        self.assertEqual(
            response2.data["name"], "Test Direct Chat"
        )  # Original name preserved

    @debug_on_failure
    def test_create_chat_room_validation(self):
        """Test chat room creation validation rules"""
        self.client.force_authenticate(user=self.teacher)

        # Test name too short
        response = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "AB",  # Less than 3 characters
                    "chat_type": "direct",
                    "participants": [self.student.id],
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)

        # Test invalid chat type
        response = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Test Chat",
                    "chat_type": "invalid_type",
                    "participants": [self.student.id],
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)

        # Test direct chat with wrong number of participants
        response = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Test Chat",
                    "chat_type": "direct",
                    "participants": [
                        self.student.id,
                        self.student2.id,
                    ],  # Should be exactly 1 participant
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)

    @debug_on_failure
    def test_create_chat_room_unauthenticated(self):
        """Test that unauthenticated users cannot create chat rooms"""
        response = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Test Chat",
                    "chat_type": "direct",
                    "participants": [self.student.id],
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_duplicate_direct_chat_logic(self):
        """
        Test that duplicate direct chats between same users return existing
        chat.
        """
        self.client.force_authenticate(user=self.teacher)

        # Create first direct chat
        response1 = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "First Chat",
                    "chat_type": "direct",
                    "participants": [self.student.id],
                },
            )
        )
        self.assertStatusCode(response1, status.HTTP_201_CREATED)
        first_chat_id = response1.data["id"]

        # Create second direct chat with same participants
        # (should return existing)
        response2 = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Second Chat",
                    "chat_type": "direct",
                    "participants": [self.student.id],
                },
            )
        )
        self.assertStatusCode(response2, status.HTTP_201_CREATED)

        # Should return the same chat room ID
        self.assertEqual(response2.data["id"], first_chat_id)

        # Verify only one chat room exists in database
        chat_rooms = ChatRoom.objects.filter(chat_type="direct")
        self.assertEqual(chat_rooms.count(), 1)

        # Verify participants are still correct
        chat_room = ChatRoom.objects.get(id=first_chat_id)
        participants = ChatParticipant.objects.filter(chat_room=chat_room)
        self.assertEqual(participants.count(), 2)  # teacher + student

    @debug_on_failure
    def test_create_chat_room_with_nonexistent_user(self):
        """Test creating chat room with non-existent user ID"""
        self.client.force_authenticate(user=self.teacher)

        response = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Test Chat",
                    "chat_type": "direct",
                    "participants": [99999],  # Non-existent user ID
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            "User with ID 99999 not found", response.data["detail"]
        )

    @debug_on_failure
    def test_list_chats_public_unauthenticated_access(self):
        """Test that unauthenticated users can see public chats only"""
        # Create a public chat
        public_chat = ChatRoom.objects.create(
            name="Public Chat",
            chat_type="group",
            created_by=self.teacher,
            is_public=True,
        )

        # Create a private chat
        private_chat = ChatRoom.objects.create(
            name="Private Chat",
            chat_type="group",
            created_by=self.teacher,
            is_public=False,
        )

        # Unauthenticated request
        response = self.log_response(self.client.get("/api/chats/"))

        self.assertStatusCode(response, status.HTTP_200_OK)
        # Should only see public chat
        chat_ids = [chat["id"] for chat in response.data["results"]]
        self.assertIn(public_chat.id, chat_ids)
        self.assertNotIn(private_chat.id, chat_ids)

    @debug_on_failure
    def test_list_chats_authenticated_user_access(self):
        """Test that authenticated users see public + their private chats"""
        self.client.force_authenticate(user=self.student)

        # Create public chat
        public_chat = ChatRoom.objects.create(
            name="Public Chat",
            chat_type="group",
            created_by=self.teacher,
            is_public=True,
        )

        # Create private chat where student is participant
        student_private_chat = ChatRoom.objects.create(
            name="Student Private Chat",
            chat_type="group",
            created_by=self.teacher,
            is_public=False,
        )
        ChatParticipant.objects.create(
            chat_room=student_private_chat,
            user=self.student,
            role="participant",
            is_active=True,
        )

        # Create private chat where student is NOT participant
        other_private_chat = ChatRoom.objects.create(
            name="Other Private Chat",
            chat_type="group",
            created_by=self.teacher,
            is_public=False,
        )

        response = self.log_response(self.client.get("/api/chats/"))

        self.assertStatusCode(response, status.HTTP_200_OK)
        chat_ids = [chat["id"] for chat in response.data["results"]]

        # Should see public chat and their private chat
        self.assertIn(public_chat.id, chat_ids)
        self.assertIn(student_private_chat.id, chat_ids)
        # Should NOT see other user's private chat
        self.assertNotIn(other_private_chat.id, chat_ids)

    @debug_on_failure
    def test_retrieve_public_chat_unauthenticated(self):
        """Test that unauthenticated users can retrieve public chats"""
        public_chat = ChatRoom.objects.create(
            name="Public Chat",
            chat_type="group",
            created_by=self.teacher,
            is_public=True,
        )

        response = self.log_response(
            self.client.get(f"/api/chats/{public_chat.id}/")
        )

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], public_chat.id)
        self.assertEqual(response.data["name"], "Public Chat")

    @debug_on_failure
    def test_retrieve_private_chat_unauthenticated_forbidden(self):
        """Test that unauthenticated users cannot retrieve private chats"""
        self.client.force_authenticate(user=self.teacher)
        private_chat = ChatRoom.objects.create(
            name="Private Chat",
            chat_type="group",
            created_by=self.teacher,
            is_public=False,
        )

        self.client.force_authenticate(None)
        response = self.log_response(
            self.client.get(f"/api/chats/{private_chat.id}/")
        )

        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_retrieve_private_chat_non_participant_forbidden(self):
        """Test that non-participants cannot retrieve private chats"""
        # Create a private chat via model (not API) to control participants
        private_chat = ChatRoom.objects.create(
            name="Teacher Private Chat",
            chat_type="group",
            created_by=self.teacher,
            is_public=False,
        )
        # Only add teacher as participant, student is not a participant
        ChatParticipant.objects.create(
            chat_room=private_chat,
            user=self.teacher,
            role="admin",
            is_active=True,
        )

        # Student (non-participant) tries to access the chat
        self.client.force_authenticate(user=self.student)
        response = self.log_response(
            self.client.get(f"/api/chats/{private_chat.id}/")
        )

        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_retrieve_private_chat_participant_access(self):
        """Test that participants can retrieve private chats"""
        self.client.force_authenticate(user=self.student)

        private_chat = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Accessible Private Chat",
                    "chat_type": "group",
                    "is_public": False,
                },
            )
        )
        self.log_response(
            self.client.post(
                f"/api/chats/{private_chat.data['id']}/participants/",
                {
                    "user": self.student.id,
                    "role": "participant",
                },
            )
        )

        response = self.log_response(
            self.client.get(f"/api/chats/{private_chat.data['id']}/")
        )

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], private_chat.data["id"])

    @debug_on_failure
    def test_update_chat_room_only_creator_allowed(self):
        """Test that only creators can update chat rooms"""
        self.client.force_authenticate(user=self.teacher)

        # Create chat room
        chat_room = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "Original Chat",
                    "chat_type": "group",
                    "is_public": True,
                },
            )
        )

        # Teacher (creator) should be able to update
        response = self.log_response(
            self.client.patch(
                f"/api/chats/{chat_room.data['id']}/", {"name": "Updated Chat"}
            )
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Chat")

        # Student (non-creator) should NOT be able to update
        self.client.force_authenticate(user=self.student)
        response = self.log_response(
            self.client.patch(
                f"/api/chats/{chat_room.data['id']}/", {"name": "Hacked Chat"}
            )
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_delete_chat_room_only_creator_allowed(self):
        """Test that only creators can delete chat rooms"""
        self.client.force_authenticate(user=self.teacher)

        # Create chat room
        chat_room = self.log_response(
            self.client.post(
                "/api/chats/",
                {
                    "name": "To Delete Chat",
                    "chat_type": "group",
                    "is_public": True,
                },
            )
        )
        chat_id = chat_room.data["id"]

        # Student (non-creator) should NOT be able to delete
        self.client.force_authenticate(user=self.student)
        response = self.log_response(
            self.client.delete(f"/api/chats/{chat_id}/")
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

        # Verify chat still exists
        self.assertTrue(ChatRoom.objects.filter(id=chat_id).exists())

        # Teacher (creator) should be able to delete
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.delete(f"/api/chats/{chat_id}/")
        )
        self.assertStatusCode(response, status.HTTP_204_NO_CONTENT)

        # Verify chat is deleted
        self.assertFalse(ChatRoom.objects.filter(id=chat_id).exists())

    @debug_on_failure
    def test_find_or_create_direct_unauthenticated_forbidden(self):
        """Test that unauthenticated users cannot use find_or_create_direct"""
        response = self.log_response(
            self.client.post(
                "/api/chats/find_or_create_direct/",
                {"username": self.student.username},
            )
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)