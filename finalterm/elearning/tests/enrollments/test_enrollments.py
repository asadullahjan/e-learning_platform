from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from elearning.models import Course, Enrollment

User = get_user_model()


class EnrollmentViewsTest(APITestCase):
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
        self.assertEqual(response.data["results"][0]["course"], self.course.id)

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
        self.assertEqual(response.data["active_enrollments"], 1)
        self.assertEqual(response.data["total_enrollments"], 1)

    def test_get_enrollments_for_student(self):
        self.client.force_authenticate(user=self.student)
        Enrollment.objects.create(
            user=self.student,
            course=self.course,
        )
        response = self.client.get("/api/enrollments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["course"], self.course.id)
