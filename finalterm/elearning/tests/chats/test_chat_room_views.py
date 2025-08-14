from rest_framework import status
from elearning.models import User, ChatRoom, ChatParticipant
from elearning.tests.test_base import BaseAPITestCase


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

    def test_create_direct_chat_room(self):
        """Test creating a direct chat room with proper participants"""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Direct Chat",
                "chat_type": "direct",
                "participants": [self.student.id],
            },
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

    def test_create_group_chat_room(self):
        """Test creating a group chat room with multiple participants"""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Group Chat",
                "chat_type": "group",
                "participants": [self.student.id, self.student2.id],
            },
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

    def test_create_direct_chat_duplicate(self):
        """Test that creating duplicate direct chats returns existing chat"""
        self.client.force_authenticate(user=self.teacher)

        # Create first chat
        response1 = self.client.post(
            "/api/chats/",
            {
                "name": "Test Direct Chat",
                "chat_type": "direct",
                "participants": [self.student.id],
            },
        )
        self.assertStatusCode(response1, status.HTTP_201_CREATED)
        first_chat_id = response1.data["id"]

        # Try to create duplicate chat
        response2 = self.client.post(
            "/api/chats/",
            {
                "name": "Another Direct Chat",
                "chat_type": "direct",
                "participants": [self.student.id],
            },
        )
        self.assertStatusCode(response2, status.HTTP_201_CREATED)

        # Should return the same chat room
        self.assertEqual(response2.data["id"], first_chat_id)
        self.assertEqual(
            response2.data["name"], "Test Direct Chat"
        )  # Original name preserved

    def test_create_chat_room_validation(self):
        """Test chat room creation validation rules"""
        self.client.force_authenticate(user=self.teacher)

        # Test name too short
        response = self.client.post(
            "/api/chats/",
            {
                "name": "AB",  # Less than 3 characters
                "chat_type": "direct",
                "participants": [self.student.id],
            },
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)

        # Test invalid chat type
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Chat",
                "chat_type": "invalid_type",
                "participants": [self.student.id],
            },
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)

        # Test direct chat with wrong number of participants
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Chat",
                "chat_type": "direct",
                "participants": [
                    self.student.id,
                    self.student2.id,
                ],  # Should be exactly 1
            },
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_chat_room_unauthenticated(self):
        """Test that unauthenticated users cannot create chat rooms"""
        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Chat",
                "chat_type": "direct",
                "participants": [self.student.id],
            },
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    def test_duplicate_direct_chat_logic(self):
        """
        Test that duplicate direct chats between same users return existing chat
        """
        self.client.force_authenticate(user=self.teacher)

        # Create first direct chat
        response1 = self.client.post(
            "/api/chats/",
            {
                "name": "First Chat",
                "chat_type": "direct",
                "participants": [self.student.id],
            },
        )
        self.assertStatusCode(response1, status.HTTP_201_CREATED)
        first_chat_id = response1.data["id"]

        # Create second direct chat with same participants
        # (should return existing)
        response2 = self.client.post(
            "/api/chats/",
            {
                "name": "Second Chat",
                "chat_type": "direct",
                "participants": [self.student.id],
            },
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

    def test_create_chat_room_with_nonexistent_user(self):
        """Test creating chat room with non-existent user ID"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            "/api/chats/",
            {
                "name": "Test Chat",
                "chat_type": "direct",
                "participants": [99999],  # Non-existent user ID
            },
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Some participant users do not exist", str(response.data)
        )
