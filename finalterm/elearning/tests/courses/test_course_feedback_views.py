from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from elearning.models import Course, CourseFeedback, User, Enrollment
from elearning.serializers import CourseFeedbackCreateUpdateSerializer
from elearning.tests.test_base import BaseTestCase, debug_on_failure


class CourseFeedbackViewsTestCase(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test users
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

        # Create test course
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
            teacher=self.teacher,
        )

        # Create enrollment for student1
        self.enrollment = Enrollment.objects.create(
            course=self.course, user=self.student1, is_active=True
        )

        # Create test feedback
        self.feedback = CourseFeedback.objects.create(
            course=self.course,
            user=self.student1,
            rating=4,
            text="This is a test feedback with more than 10 characters",
        )

        # Setup API client
        self.client = APIClient()

        # URLs
        self.feedback_list_url = reverse(
            "elearning:course-feedbacks-list",
            kwargs={"course_pk": self.course.id},
        )
        self.feedback_detail_url = reverse(
            "elearning:course-feedbacks-detail",
            kwargs={"course_pk": self.course.id, "pk": self.feedback.id},
        )

    @debug_on_failure
    def test_create_feedback_not_authenticated(self):
        """Test that unauthenticated users cannot create feedback"""
        data = {
            "rating": 5,
            "text": "This is a test feedback with more than 10 characters",
        }
        response = self.log_response(
            self.client.post(self.feedback_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_create_feedback_not_enrolled(self):
        """Test that non-enrolled users cannot create feedback"""
        self.client.force_authenticate(user=self.student2)

        data = {
            "rating": 5,
            "text": "This is a test feedback with more than 10 characters",
        }
        response = self.log_response(
            self.client.post(self.feedback_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_create_feedback_enrolled_user(self):
        """Test that enrolled users can create feedback"""
        # Use student2 (who is not enrolled) and enroll them first
        Enrollment.objects.create(
            course=self.course, user=self.student2, is_active=True
        )

        self.client.force_authenticate(user=self.student2)

        data = {
            "rating": 5,
            "text": (
                "This is another test feedback with more than " "10 characters"
            ),
        }
        response = self.log_response(
            self.client.post(self.feedback_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CourseFeedback.objects.count(), 2)

    @debug_on_failure
    def test_create_feedback_duplicate(self):
        """Test that users cannot create duplicate feedback for the same course"""
        self.client.force_authenticate(user=self.student1)

        data = {
            "rating": 3,
            "text": "This is a duplicate feedback with more than 10 characters",
        }
        response = self.client.post(self.feedback_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "already left feedback", response.data["non_field_errors"][0]
        )

        # Verify only one feedback exists for this user
        self.assertEqual(
            CourseFeedback.objects.filter(
                user=self.student1, course=self.course
            ).count(),
            1,
        )

    @debug_on_failure
    def test_create_feedback_invalid_rating(self):
        """Test feedback creation with invalid rating"""
        self.client.force_authenticate(user=self.student1)

        data = {
            "rating": 6,  # Invalid rating
            "text": "This is a test feedback with more than 10 characters",
        }
        response = self.log_response(
            self.client.post(self.feedback_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @debug_on_failure
    def test_create_feedback_text_too_short(self):
        """Test feedback creation with text too short"""
        self.client.force_authenticate(user=self.student1)

        data = {"rating": 5, "text": "Short"}  # Less than 10 characters
        response = self.log_response(
            self.client.post(self.feedback_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("at least 10 characters", response.data["text"][0])

    @debug_on_failure
    def test_create_feedback_text_too_long(self):
        """Test feedback creation with text too long"""
        self.client.force_authenticate(user=self.student1)

        data = {"rating": 5, "text": "A" * 501}  # More than 500 characters
        response = self.log_response(
            self.client.post(self.feedback_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cannot exceed 500 characters", response.data["text"][0])

    @debug_on_failure
    def test_update_feedback_owner(self):
        """Test that feedback owner can update their feedback"""
        self.client.force_authenticate(user=self.student1)

        data = {
            "rating": 5,
            "text": "This is an updated feedback with more than 10 characters",
        }
        response = self.log_response(
            self.client.patch(self.feedback_detail_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["text"], data["text"])

    @debug_on_failure
    def test_update_feedback_not_owner(self):
        """Test that non-owners cannot update feedback"""
        self.client.force_authenticate(user=self.student2)

        data = {
            "rating": 5,
            "text": "This is an updated feedback with more than 10 characters",
        }
        response = self.log_response(
            self.client.patch(self.feedback_detail_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CourseFeedback.objects.count(), 1)

    @debug_on_failure
    def test_delete_feedback_owner(self):
        """Test that feedback owner can delete their feedback"""
        self.client.force_authenticate(user=self.student1)

        response = self.log_response(
            self.client.delete(self.feedback_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CourseFeedback.objects.count(), 0)

    @debug_on_failure
    def test_delete_feedback_not_owner(self):
        """Test that non-owners cannot delete feedback"""
        self.client.force_authenticate(user=self.student2)

        response = self.log_response(
            self.client.delete(self.feedback_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(CourseFeedback.objects.count(), 1)

    @debug_on_failure
    def test_feedback_serializer_validation(self):
        """Test serializer validation methods"""
        serializer = CourseFeedbackCreateUpdateSerializer(
            data={
                "rating": 5,
                "text": "Valid feedback text with more than 10 characters",
            }
        )
        self.assertTrue(serializer.is_valid())

    @debug_on_failure
    def test_feedback_serializer_invalid_rating(self):
        """Test serializer rating validation"""
        serializer = CourseFeedbackCreateUpdateSerializer(
            data={
                "rating": 0,  # Invalid rating
                "text": "Valid feedback text with more than 10 characters",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    @debug_on_failure
    def test_feedback_serializer_text_too_short(self):
        """Test serializer text length validation"""
        serializer = CourseFeedbackCreateUpdateSerializer(
            data={"rating": 5, "text": "Short"}  # Too short
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)

    @debug_on_failure
    def test_feedback_serializer_text_too_long(self):
        """Test serializer text length validation"""
        serializer = CourseFeedbackCreateUpdateSerializer(
            data={"rating": 5, "text": "A" * 501}  # Too long
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)

    @debug_on_failure
    def test_feedback_list_serializer_fields(self):
        """Test that feedback list serializer includes correct fields"""
        response = self.log_response(self.client.get(self.feedback_list_url))
        feedback_data = response.data["results"][0]

        expected_fields = ["id", "rating", "text", "created_at", "user"]
        for field in expected_fields:
            self.assertIn(field, feedback_data)

    @debug_on_failure
    def test_feedback_user_data_included(self):
        """Test that user data is included in feedback list"""
        response = self.log_response(self.client.get(self.feedback_list_url))
        feedback_data = response.data["results"][0]

        self.assertIn("user", feedback_data)
        self.assertEqual(feedback_data["user"]["username"], "student1")
        self.assertEqual(feedback_data["user"]["role"], "student")

    @debug_on_failure
    def test_course_not_found(self):
        """Test feedback creation for non-existent course"""
        self.client.force_authenticate(user=self.student1)

        invalid_url = reverse(
            "elearning:course-feedbacks-list", kwargs={"course_pk": 99999}
        )
        data = {
            "rating": 5,
            "text": "This is a test feedback with more than 10 characters",
        }
        response = self.log_response(self.client.post(invalid_url, data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_feedback_creation_with_inactive_enrollment(self):
        """Test that users with inactive enrollment cannot create feedback"""
        # Deactivate enrollment
        self.enrollment.is_active = False
        self.enrollment.save()

        self.client.force_authenticate(user=self.student1)

        data = {
            "rating": 5,
            "text": "This is a test feedback with more than 10 characters",
        }
        response = self.log_response(
            self.client.post(self.feedback_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
