from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from elearning.models import ChatRoom, ChatParticipant, Course
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure

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

    @debug_on_failure
    def test_create_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.log_response(self.client.post(
            "/api/courses/",
            {
                "title": "Test Course",
                "description": description,
            },
        ))
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.first().title, "Test Course")
        self.assertEqual(Course.objects.first().description, description)

    @debug_on_failure
    def test_create_course_by_non_teacher(self):
        self.client.force_authenticate(user=self.student)
        description = "Test Description, adding more text to get 20 characters"
        response = self.log_response(self.client.post(
            "/api/courses/",
            {"title": "Test Course", "description": description},
        ))
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Course.objects.count(), 0)

    @debug_on_failure
    def test_create_course_with_short_title(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.log_response(self.client.post(
            "/api/courses/",
            {"title": "Test", "description": description},
        ))
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Course.objects.count(), 0)

    @debug_on_failure
    def test_create_course_with_short_description(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(self.client.post(
            "/api/courses/",
            {"title": "Test Course", "description": "Short"},
        ))
        self.assertStatusCode(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Course.objects.count(), 0)

    @debug_on_failure
    def test_partial_update_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        response = self.log_response(self.client.patch(
            f"/api/courses/{course.id}/",
            {"title": "Updated Course", "description": description},
        ))
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(Course.objects.first().title, "Updated Course")

    @debug_on_failure
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
        response = self.log_response(self.client.put(
            f"/api/courses/{course.id}/",
            {
                "title": "Updated Course",
                "description": updated_description,
            },
        ))
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(Course.objects.first().title, "Updated Course")
        self.assertEqual(
            Course.objects.first().description, updated_description
        )

    @debug_on_failure
    def test_delete_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        response = self.log_response(
            self.client.delete(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)

    @debug_on_failure
    def test_get_course_list(self):
        description = "Test Description, adding more text to get 20 characters"
        Course.objects.create(
            title="Test Course 1",
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
        response = self.log_response(self.client.get("/api/courses/"))
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    @debug_on_failure
    def test_teacher_cannot_edit_other_teacher_course(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher2,
            published_at=timezone.now(),
        )
        response = self.log_response(
            self.client.patch(
                f"/api/courses/{course.id}/",
                {"title": "Updated Course"},
            )
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_unauthenticated_can_view_courses(self):
        description = "Test Description, adding more text to get 20 characters"
        Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        response = self.log_response(self.client.get("/api/courses/"))
        self.assertStatusCode(response, status.HTTP_200_OK)

    @debug_on_failure
    def test_retrieve_published_course_unauthenticated(self):
        """Test that unauthenticated users can retrieve published courses"""
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Public Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        response = self.log_response(
            self.client.get(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Public Course")

    @debug_on_failure
    def test_retrieve_unpublished_course_unauthenticated_forbidden(
        self
    ):
        """Test that unauthenticated users cannot retrieve unpublished courses"""
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Private Course",
            description=description,
            teacher=self.teacher,
            published_at=None,
        )
        response = self.log_response(
            self.client.get(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_retrieve_unpublished_course_by_owner_allowed(self):
        """Test that course owners can retrieve their unpublished courses"""
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="My Draft Course",
            description=description,
            teacher=self.teacher,
            published_at=None,
        )
        response = self.log_response(
            self.client.get(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "My Draft Course")

    @debug_on_failure
    def test_retrieve_unpublished_course_by_non_owner_forbidden(self):
        """Test that non-owners cannot retrieve unpublished courses"""
        self.client.force_authenticate(user=self.teacher2)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Another Teacher Course",
            description=description,
            teacher=self.teacher,
            published_at=None,
        )
        response = self.log_response(
            self.client.get(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_delete_course_only_owner_allowed(self):
        """Test that only course owners can delete courses"""
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="To Delete Course",
            description=description,
            teacher=self.teacher,
        )
        course_id = course.id

        # Owner should be able to delete
        response = self.log_response(
            self.client.delete(f"/api/courses/{course_id}/")
        )
        self.assertStatusCode(response, status.HTTP_204_NO_CONTENT)

        # Verify course is deleted
        self.assertFalse(Course.objects.filter(id=course_id).exists())

    @debug_on_failure
    def test_delete_course_by_non_owner_forbidden(self):
        """Test that non-owners cannot delete courses"""
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Protected Course",
            description=description,
            teacher=self.teacher,
        )
        course_id = course.id

        # Different teacher should NOT be able to delete
        self.client.force_authenticate(user=self.teacher2)
        response = self.log_response(
            self.client.delete(f"/api/courses/{course_id}/")
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

        # Verify course still exists
        self.assertTrue(Course.objects.filter(id=course_id).exists())

    @debug_on_failure
    def test_create_course_unauthenticated_forbidden(self):
        """Test that unauthenticated users cannot create courses"""
        description = "Test Description, adding more text to get 20 characters"
        response = self.log_response(
            self.client.post(
                "/api/courses/",
                {
                    "title": "Unauthorized Course",
                    "description": description,
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_chatroom_creation_on_course_creation(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.log_response(
            self.client.post(
                "/api/courses/",
                {
                    "title": "Test Course",
                    "description": description,
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        course = Course.objects.get(id=response.data["id"])
        self.assertTrue(ChatRoom.objects.filter(course=course).exists())

    @debug_on_failure
    def test_chatroom_participant_creation_on_course_creation(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        response = self.log_response(
            self.client.post(
                "/api/courses/",
                {
                    "title": "Test Course",
                    "description": description,
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        course = Course.objects.get(id=response.data["id"])
        chatroom = ChatRoom.objects.get(course=course)
        self.assertTrue(
            ChatParticipant.objects.filter(
                chat_room=chatroom, user=self.teacher
            ).exists()
        )

    @debug_on_failure
    def test_chatroom_deletion_when_course_deleted(self):
        self.client.force_authenticate(user=self.teacher)
        description = "Test Description, adding more text to get 20 characters"
        course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        chatroom = ChatRoom.objects.create(
            name="Test Chat Room",
            course=course,
            created_by=self.teacher,
            chat_type="course",
        )
        response = self.log_response(
            self.client.delete(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ChatRoom.objects.filter(id=chatroom.id).exists())
