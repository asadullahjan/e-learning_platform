from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Course, Enrollment
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure

User = get_user_model()


class EnrollmentViewsTest(BaseAPITestCase):
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
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        self.course2 = Course.objects.create(
            title="Test Course 2",
            description="Test Description 2",
            teacher=self.teacher,
        )

    def test_enroll_in_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            "/api/enrollments/", {"course": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["course"], self.course.id)
        self.assertEqual(response.data["user"], self.student.id)

    def test_enroll_in_unpublished_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            "/api/enrollments/", {"course": self.course2.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enroll_in_course_unauthenticated(self):
        response = self.client.post(
            "/api/enrollments/", {"course": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_enrollments_for_course_owner(self):
        self.client.force_authenticate(user=self.teacher)
        Enrollment.objects.create(
            user=self.student,
            course=self.course,
        )
        Enrollment.objects.create(
            user=self.student,
            course=self.course2,
        )
        response = self.client.get(
            "/api/enrollments/", {"course": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["user"]["id"], self.student.id
        )

    def test_get_enrollments_for_course_for_student(self):
        self.client.force_authenticate(user=self.student)
        Enrollment.objects.create(
            user=self.student,
            course=self.course,
        )
        response = self.client.get(
            "/api/enrollments/", {"course": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Non-owners get empty list (no access to other course enrollments)
        self.assertEqual(response.data["count"], 0)

    def test_get_enrollments_for_student(self):
        self.client.force_authenticate(user=self.student)
        Enrollment.objects.create(
            user=self.student,
            course=self.course,
        )
        response = self.client.get("/api/enrollments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["course"]["id"], self.course.id
        )

    @debug_on_failure
    def test_get_enrollments_for_teacher(self):
        """Test that teachers can view their own enrollments with course
        details"""
        self.client.force_authenticate(user=self.teacher)
        # Create a course taught by another teacher
        other_teacher = User.objects.create_user(
            username="otherteacher",
            email="other@example.com",
            password="testpass123",
            role="teacher",
        )
        other_course = Course.objects.create(
            title="Other Course",
            description="Other Description",
            teacher=other_teacher,
            published_at=timezone.now(),
        )
        # Enroll the teacher in the other course
        Enrollment.objects.create(
            user=self.teacher,
            course=other_course,
        )

        response = self.log_response(self.client.get("/api/enrollments/"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["course"]["id"], other_course.id
        )
        # Verify course details are included (not user details)
        self.assertIn("course", response.data["results"][0])
        self.assertNotIn("user", response.data["results"][0])
