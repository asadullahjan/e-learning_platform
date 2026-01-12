from django.utils import timezone
from rest_framework import status
from elearning.models import Course, CourseFeedback, User, Enrollment
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure


class CourseFeedbackViewsTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        # Users
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@test.com",
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

        # Course + enrollment + feedback
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Desc",
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        Enrollment.objects.create(
            course=self.course, user=self.student1, is_active=True
        )
        self.feedback = CourseFeedback.objects.create(
            course=self.course,
            user=self.student1,
            rating=4,
            text="This is a valid feedback with more than 10 chars",
        )

        # URLs
        self.feedback_list_url = f"/api/courses/{self.course.id}/feedbacks/"
        self.feedback_detail_url = (
            f"/api/courses/{self.course.id}/feedbacks/{self.feedback.id}/"
        )

    @debug_on_failure
    def test_enrolled_user_can_create_feedback(self):
        Enrollment.objects.create(
            course=self.course, user=self.student2, is_active=True
        )
        self.client.force_authenticate(user=self.student2)

        response = self.client.post(
            self.feedback_list_url,
            {"rating": 5, "text": "Another valid feedback text"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CourseFeedback.objects.count(), 2)

    @debug_on_failure
    def test_non_enrolled_user_cannot_create_feedback(self):
        self.client.force_authenticate(user=self.student2)
        response = self.client.post(
            self.feedback_list_url,
            {"rating": 5, "text": "Not enrolled feedback"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_user_cannot_create_duplicate_feedback(self):
        self.client.force_authenticate(user=self.student1)
        response = self.client.post(
            self.feedback_list_url,
            {"rating": 3, "text": "Duplicate feedback attempt"},
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    @debug_on_failure
    def test_owner_can_update_and_delete_feedback(self):
        self.client.force_authenticate(user=self.student1)

        # Update
        response = self.client.patch(
            self.feedback_detail_url,
            {"rating": 5, "text": "Updated feedback text"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete
        response = self.client.delete(self.feedback_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @debug_on_failure
    def test_non_owner_cannot_update_or_delete_feedback(self):
        self.client.force_authenticate(user=self.student2)

        # Update
        response = self.client.patch(
            self.feedback_detail_url, {"rating": 5, "text": "Hacked feedback"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Delete
        response = self.client.delete(self.feedback_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_cannot_create_feedback_for_unpublished_course(self):
        unpublished = Course.objects.create(
            title="Unpublished",
            description="Hidden",
            teacher=self.teacher,
            published_at=None,
        )
        Enrollment.objects.create(
            course=unpublished, user=self.student1, is_active=True
        )

        self.client.force_authenticate(user=self.student1)
        url = f"/api/courses/{unpublished.id}/feedbacks/"

        response = self.client.post(
            url, {"rating": 5, "text": "Feedback on unpublished course"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @debug_on_failure
    def test_feedback_list_returns_user_data(self):
        response = self.client.get(self.feedback_list_url)
        feedback_data = response.data["results"][0]

        self.assertIn("id", feedback_data)
        self.assertIn("rating", feedback_data)
        self.assertIn("text", feedback_data)
        self.assertIn("user", feedback_data)
        self.assertEqual(feedback_data["user"]["username"], "student1")
