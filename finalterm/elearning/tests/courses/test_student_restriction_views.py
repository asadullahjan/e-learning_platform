from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from elearning.models import User, Course, StudentRestriction, Enrollment
from elearning.tests.test_base import BaseTestCase, debug_on_failure


class StudentRestrictionViewsTestCase(BaseTestCase):
    """
    Test case for student restriction views.
    """

    def setUp(self):
        """Set up test data."""
        # Create users
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

        # Create courses
        course_description = (
            "Test Description, adding more text to get 20 characters"
        )
        self.course1 = Course.objects.create(
            title="Test Course 1",
            description=course_description,
            teacher=self.teacher1,
        )

        self.course2 = Course.objects.create(
            title="Test Course 2",
            description=course_description,
            teacher=self.teacher1,
        )

        # Create enrollments
        self.enrollment1 = Enrollment.objects.create(
            course=self.course1, user=self.student1, is_active=True
        )

        self.enrollment2 = Enrollment.objects.create(
            course=self.course2, user=self.student1, is_active=True
        )

        # Create initial restriction
        self.restriction1 = StudentRestriction.objects.create(
            teacher=self.teacher1,
            student=self.student1,
            course=self.course1,
            reason="Test restriction",
        )

        # Set up API client
        self.client = APIClient()

        # URLs
        self.restrictions_list_url = reverse("elearning:restriction-list")
        self.restriction_detail_url = reverse(
            "elearning:restriction-detail", kwargs={"pk": self.restriction1.pk}
        )
        self.check_student_url = reverse("elearning:restriction-check-student")

    @debug_on_failure
    def test_get_restrictions_list_student(self):
        """Test that students cannot access restrictions list."""
        self.client.force_authenticate(user=self.student1)
        response = self.log_response(
            self.client.get(self.restrictions_list_url)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_get_restrictions_list_teacher(self):
        """Test that teachers can access their own restrictions list."""
        self.client.force_authenticate(user=self.teacher1)
        response = self.log_response(
            self.client.get(self.restrictions_list_url)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"], self.restriction1.pk
        )

    @debug_on_failure
    def test_get_restrictions_list_other_teacher(self):
        """Test that teachers only see their own restrictions."""
        self.client.force_authenticate(user=self.teacher2)
        response = self.log_response(
            self.client.get(self.restrictions_list_url)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    @debug_on_failure
    def test_create_restriction_not_authenticated(self):
        """Test that unauthenticated users cannot create restrictions."""
        data = {
            "student_id": self.student2.id,
            "course_id": self.course1.id,
            "reason": "Test restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_create_restriction_student(self):
        """Test that students cannot create restrictions."""
        self.client.force_authenticate(user=self.student1)
        data = {
            "student_id": self.student2.id,
            "course_id": self.course1.id,
            "reason": "Test restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_create_restriction_teacher_success(self):
        """Test that teachers can create restrictions successfully."""
        self.client.force_authenticate(user=self.teacher1)
        Enrollment.objects.create(
            course=self.course1, user=self.student2, is_active=True
        )
        data = {
            "student_id": self.student2.id,
            "course_id": self.course1.id,
            "reason": "Test restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentRestriction.objects.count(), 2)

        # Check that enrollment was deactivated
        enrollment = Enrollment.objects.get(
            course=self.course1, user=self.student2
        )
        self.assertFalse(enrollment.is_active)

    @debug_on_failure
    def test_create_restriction_duplicate(self):
        """Test that duplicate restrictions cannot be created."""
        self.client.force_authenticate(user=self.teacher1)
        data = {
            "student_id": self.student1.id,
            "course_id": self.course1.id,
            "reason": "Duplicate restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", response.data["non_field_errors"][0])

    @debug_on_failure
    def test_create_restriction_self(self):
        """Test that teachers cannot restrict themselves."""
        self.client.force_authenticate(user=self.teacher1)
        data = {
            "student_id": self.teacher1.id,
            "course_id": self.course1.id,
            "reason": "Self restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Cannot restrict yourself", response.data["non_field_errors"][0]
        )

    @debug_on_failure
    def test_delete_restriction_owner(self):
        """Test that restriction owners can delete restrictions."""
        self.client.force_authenticate(user=self.teacher1)
        response = self.log_response(
            self.client.delete(self.restriction_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StudentRestriction.objects.count(), 0)

        # Check that enrollment was reactivated
        enrollment = Enrollment.objects.get(
            course=self.course1, user=self.student1
        )
        self.assertTrue(enrollment.is_active)

    @debug_on_failure
    def test_delete_restriction_non_owner(self):
        """Test that non-owners cannot delete restrictions."""
        self.client.force_authenticate(user=self.teacher2)
        response = self.log_response(
            self.client.delete(self.restriction_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(StudentRestriction.objects.count(), 1)

    @debug_on_failure
    def test_check_student_restricted(self):
        """Test checking if a student is restricted."""
        self.client.force_authenticate(user=self.teacher1)
        response = self.log_response(
            self.client.get(
                self.check_student_url,
                {"student_id": self.student1.id, "course_id": self.course1.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_restricted"])

    @debug_on_failure
    def test_check_student_not_restricted(self):
        """Test checking if a student is not restricted."""
        self.client.force_authenticate(user=self.teacher1)
        response = self.log_response(
            self.client.get(
                self.check_student_url,
                {"student_id": self.student2.id, "course_id": self.course1.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_restricted"])
