from unittest.mock import patch
from rest_framework import status

from elearning.models import (
    User,
    Course,
    StudentRestriction,
    Enrollment,
    ChatParticipant,
    ChatRoom,
)
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure


@patch(
    "elearning.services.notification_service."
    "NotificationService._send_websocket_message"
)
class CourseStudentRestrictionViewsTestCase(BaseAPITestCase):
    """Tests for student restrictions affecting enrollments and chat
    participation with permissions."""

    def setUp(self, mock_notification=None):
        super().setUp()

        # Users
        self.teacher1 = User.objects.create_user(
            username="teacher1",
            email="teacher1@test.com",
            password="testpass123",
            role="teacher",
        )
        self.teacher2 = User.objects.create_user(
            username="teacher2",
            email="teacher2@test.com",
            password="testpass123",
            role="teacher",
        )
        self.student1 = User.objects.create_user(
            username="student1",
            email="student1@test.com",
            password="testpass123",
            role="student",
        )
        self.student2 = User.objects.create_user(
            username="student2",
            email="student2@test.com",
            password="testpass123",
            role="student",
        )

        # Courses
        from django.utils import timezone

        self.course1 = Course.objects.create(
            title="Course 1",
            description="Test Course 1",
            teacher=self.teacher1,
            published_at=timezone.now(),
        )
        self.course2 = Course.objects.create(
            title="Course 2",
            description="Test Course 2",
            teacher=self.teacher1,
            published_at=timezone.now(),
        )

        # Enrollments
        self.enrollment1 = Enrollment.objects.create(
            course=self.course1, user=self.student1, is_active=True
        )
        self.enrollment2 = Enrollment.objects.create(
            course=self.course2, user=self.student1, is_active=True
        )

        # Chat rooms
        self.course1_chatroom = ChatRoom.objects.create(
            course=self.course1, chat_type="course", created_by=self.teacher1
        )
        self.course2_chatroom = ChatRoom.objects.create(
            course=self.course2, chat_type="course", created_by=self.teacher1
        )

        # Chat participants
        self.chat_participant1 = ChatParticipant.objects.create(
            chat_room=self.course1_chatroom,
            user=self.student1,
            is_active=True,
        )
        self.chat_participant2 = ChatParticipant.objects.create(
            chat_room=self.course2_chatroom,
            user=self.student1,
            is_active=True,
        )

        # URLs
        self.restrictions_url_course1 = (
            f"/api/courses/{self.course1.id}/restrictions/"
        )
        self.restrictions_url_course2 = (
            f"/api/courses/{self.course2.id}/restrictions/"
        )
        self.enrollments_url_course1 = (
            f"/api/courses/{self.course1.id}/enrollments/"
        )
        self.enrollments_url_course2 = (
            f"/api/courses/{self.course2.id}/enrollments/"
        )

    @debug_on_failure
    def test_teacher_can_create_restriction_and_affects_enrollment_chat(
        self, mock_notification
    ):
        """Teacher creates restriction → enrollment & chat inactive."""
        self.client.force_authenticate(user=self.teacher1)
        data = {
            "student": self.student1.id,
            "course": self.course1.id,
            "reason": "Restricted",
        }

        resp = self.log_response(
            self.client.post(self.restrictions_url_course1, data)
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Enrollment inactive
        self.enrollment1.refresh_from_db()
        self.assertFalse(self.enrollment1.is_active)
        print("enrollment1", self.enrollment1.is_active, self.enrollment1.id)
        # Chat inactive
        self.chat_participant1.refresh_from_db()
        self.assertFalse(self.chat_participant1.is_active)
        print("chat_participant1", self.chat_participant1.is_active)
        # Other enrollment/chat unaffected
        self.enrollment2.refresh_from_db()
        self.assertTrue(self.enrollment2.is_active)
        print("enrollment2", self.enrollment2.is_active)
        self.chat_participant2.refresh_from_db()
        self.assertTrue(self.chat_participant2.is_active)
        print("chat_participant2", self.chat_participant2.is_active)

    @debug_on_failure
    def test_student_cannot_create_restriction(self, mock_notification):
        """Students cannot create restrictions."""
        self.client.force_authenticate(user=self.student1)
        data = {
            "student": self.student2.id,
            "course": self.course1.id,
            "reason": "Restricted",
        }
        resp = self.log_response(
            self.client.post(self.restrictions_url_course1, data)
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_other_teacher_cannot_create_restriction_for_diff_teacher_courses(
        self, mock_notification
    ):
        """
        Other teachers cannot restrict students in courses they don't own.
        """
        self.client.force_authenticate(user=self.teacher2)
        data = {
            "student": self.student1.id,
            "course": self.course1.id,
            "reason": "Restricted",
        }
        resp = self.log_response(
            self.client.post(self.restrictions_url_course1, data)
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_restricted_student_cannot_enroll_or_reactivate(
        self, mock_notification
    ):
        """
        Restricted students cannot enroll or reactivate existing enrollments.
        """
        # Global restriction
        StudentRestriction.objects.create(
            teacher=self.teacher1,
            student=self.student2,
            course=None,
            reason="Global restriction",
        )
        self.client.force_authenticate(user=self.student2)

        resp = self.log_response(
            self.client.post(self.enrollments_url_course1, {})
        )
        self.assertIn("restricted", resp.data["detail"].lower())
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.log_response(
            self.client.post(self.enrollments_url_course2, {})
        )
        self.assertIn("restricted", resp.data["detail"].lower())
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_only_owner_teacher_can_delete_restriction(
        self, mock_notification
    ):
        """Only teacher who created restriction can delete it."""
        restriction = StudentRestriction.objects.create(
            teacher=self.teacher1,
            student=self.student1,
            course=self.course1,
            reason="Test",
        )

        # Non-owner teacher cannot delete
        self.client.force_authenticate(user=self.teacher2)
        delete_url = (
            f"/api/courses/{self.course1.id}/restrictions/{restriction.pk}/"
        )
        resp = self.log_response(self.client.delete(delete_url))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Owner teacher can delete
        self.client.force_authenticate(user=self.teacher1)
        resp = self.log_response(self.client.delete(delete_url))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
