from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from ..models import ChatRoom, ChatParticipant, Course
from elearning.tests.test_base import BaseAPITestCase

User = get_user_model()


class CourseViewsTest(BaseAPITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
            role="student",
        )
        self.teacher2 = User.objects.create_user(
            username="testuser3",
            email="test3@example.com",
            password="testpass123",
            role="teacher",
        )

    def test_create_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.client.post(
            "/api/courses/",
            {
                "title": "Test Course",
                "description": description,
            },
        )
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.first().title, "Test Course")
        self.assertEqual(Course.objects.first().description, description)

    def test_create_course_by_non_teacher(self):
        self.client.force_authenticate(user=self.student)
        description = "Test Description, adding more text to get 20 characters"
        response = self.client.post(
            "/api/courses/",
            {"title": "Test Course", "description": description},
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Course.objects.count(), 0)

    def test_create_course_with_short_title(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.client.post(
            "/api/courses/",
            {"title": "Test", "description": description},
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Course.objects.count(), 0)

    def test_create_course_with_short_description(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(
            "/api/courses/",
            {"title": "Test Course", "description": "Short"},
        )
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Course.objects.count(), 0)

    def test_partial_update_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        response = self.client.patch(
            f"/api/courses/{course.id}/",
            {"title": "Updated Course", "description": description},
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(Course.objects.first().title, "Updated Course")

    def test_full_update_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        updated_description = (
            "Updated Description, adding more text to get 20 characters"
        )
        course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        response = self.client.put(
            f"/api/courses/{course.id}/",
            {"title": "Updated Course", "description": updated_description},
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(Course.objects.first().title, "Updated Course")
        self.assertEqual(
            Course.objects.first().description, updated_description
        )

    def test_delete_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        response = self.client.delete(f"/api/courses/{course.id}/")
        self.assertStatusCode(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)

    def test_get_course_list(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        Course.objects.create(
            title="Test Course 2",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        response = self.client.get("/api/courses/")
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_teacher_cannot_edit_other_teacher_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher2,
            published_at=timezone.now(),
        )
        response = self.client.patch(
            f"/api/courses/{course.id}/", {"title": "Updated Course"}
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_can_view_courses(self):
        response = self.client.get("/api/courses/")
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_chatroom_creation_on_course_creation(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.client.post(
            "/api/courses/",
            {"title": "Test Course", "description": description},
        )
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        self.assertEqual(ChatRoom.objects.count(), 1)
        self.assertEqual(ChatRoom.objects.first().name, "Test Course Chat")
        self.assertEqual(
            ChatRoom.objects.first().course.id, response.data["id"]
        )
        self.assertEqual(ChatRoom.objects.first().chat_type, "course")
        self.assertEqual(ChatRoom.objects.first().is_public, True)
        self.assertEqual(ChatRoom.objects.first().created_by, self.teacher)

    def test_chatroom_participant_creation_on_course_creation(self):
        """Test that course creator is added as admin participant"""
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.client.post(
            "/api/courses/",
            {"title": "Test Course", "description": description},
        )
        self.assertStatusCode(response, status.HTTP_201_CREATED)

        # Check that creator is added as admin participant
        chatroom = ChatRoom.objects.first()
        participant = ChatParticipant.objects.get(
            chat_room=chatroom, user=self.teacher
        )
        self.assertEqual(participant.role, "admin")

    def test_chatroom_deletion_when_course_deleted(self):
        """Test that chatroom is deleted when course is deleted"""
        # Create course (which creates chatroom)
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.client.post(
            "/api/courses/",
            {"title": "Test Course", "description": description},
        )
        course_id = response.data["id"]

        # Verify chatroom exists
        self.assertEqual(ChatRoom.objects.count(), 1)

        # Delete course
        response = self.client.delete(f"/api/courses/{course_id}/")
        self.assertStatusCode(response, status.HTTP_204_NO_CONTENT)

        # Verify chatroom is also deleted (due to CASCADE)
        self.assertEqual(ChatRoom.objects.count(), 0)
