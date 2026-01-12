from rest_framework import status

from elearning.models import ChatRoom, ChatParticipant, Course, User
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure


class CourseViewsTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.teacher = User.objects.create_user(
            username="teacher1",
            email="teacher1@example.com",
            password="testpass",
            role="teacher",
        )
        self.teacher2 = User.objects.create_user(
            username="teacher2",
            email="teacher2@example.com",
            password="testpass",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="student1",
            email="student1@example.com",
            password="testpass",
            role="student",
        )

    @debug_on_failure
    def test_teacher_can_create_course(self):
        description = "Valid course description longer than 20 chars"
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.post(
                "/api/courses/",
                {"title": "Course 1", "description": description},
            )
        )
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        course = Course.objects.first()
        self.assertEqual(course.title, "Course 1")
        self.assertEqual(course.teacher, self.teacher)

    @debug_on_failure
    def test_non_teacher_cannot_create_course(self):
        self.client.force_authenticate(user=self.student)
        description = "Valid description"
        response = self.log_response(
            self.client.post(
                "/api/courses/",
                {"title": "Course 2", "description": description},
            )
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Course.objects.count(), 0)

    @debug_on_failure
    def test_teacher_can_update_own_course(self):
        self.client.force_authenticate(user=self.teacher)
        course = Course.objects.create(
            title="Original Course",
            description="Original Description 123",
            teacher=self.teacher,
        )
        updated_desc = "Updated Description 123"
        response = self.log_response(
            self.client.patch(
                f"/api/courses/{course.id}/",
                {"title": "Updated Course", "description": updated_desc},
            )
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.title, "Updated Course")
        self.assertEqual(course.description, updated_desc)

    @debug_on_failure
    def test_teacher_cannot_update_others_course(self):
        self.client.force_authenticate(user=self.teacher)
        course = Course.objects.create(
            title="Other Teacher Course",
            description="Description",
            teacher=self.teacher2,
        )
        response = self.log_response(
            self.client.patch(
                f"/api/courses/{course.id}/",
                {"title": "Hacked Course"},
            )
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_teacher_can_delete_own_course(self):
        self.client.force_authenticate(user=self.teacher)
        course = Course.objects.create(
            title="Course To Delete",
            description="Description",
            teacher=self.teacher,
        )
        response = self.log_response(
            self.client.delete(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=course.id).exists())

    @debug_on_failure
    def test_non_owner_cannot_delete_course(self):
        self.client.force_authenticate(user=self.teacher)
        course = Course.objects.create(
            title="Protected Course",
            description="Description",
            teacher=self.teacher2,
        )
        response = self.log_response(
            self.client.delete(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_retrieve_unpublished_course_owner_allowed(self):
        course = Course.objects.create(
            title="Draft Course",
            description="Desc",
            teacher=self.teacher,
            published_at=None,
        )
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.get(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_200_OK)

    @debug_on_failure
    def test_retrieve_unpublished_course_non_owner_forbidden(self):
        course = Course.objects.create(
            title="Draft Course",
            description="Desc",
            teacher=self.teacher,
            published_at=None,
        )
        self.client.force_authenticate(user=self.teacher2)
        response = self.log_response(
            self.client.get(f"/api/courses/{course.id}/")
        )
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_chatroom_created_with_course(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.log_response(
            self.client.post(
                "/api/courses/",
                {
                    "title": "Course With Chat",
                    "description": "Desc Longer Than 20 chars",
                },
            )
        )
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        course = Course.objects.get(id=response.data["id"])
        self.assertTrue(ChatRoom.objects.filter(course=course).exists())
        chatroom = ChatRoom.objects.get(course=course)
        self.assertTrue(
            ChatParticipant.objects.filter(
                chat_room=chatroom, user=self.teacher
            ).exists()
        )
