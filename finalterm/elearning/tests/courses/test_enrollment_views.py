from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from elearning.models import Course, Enrollment
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

    @debug_on_failure
    def test_enroll_in_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.log_response(
            self.client.post(f"/api/courses/{self.course.id}/enrollments/", {})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["course"], self.course.id)
        self.assertEqual(response.data["user"], self.student.id)

    @debug_on_failure
    def test_enroll_in_unpublished_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.log_response(
            self.client.post(
                f"/api/courses/{self.course2.id}/enrollments/", {}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @debug_on_failure
    def test_enroll_in_course_unauthenticated(self):
        response = self.log_response(
            self.client.post(f"/api/courses/{self.course.id}/enrollments/", {})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
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
        response = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/enrollments/")
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["user"]["id"], self.student.id
        )

    @debug_on_failure
    def test_get_enrollments_for_course_for_student(self):
        self.client.force_authenticate(user=self.student)
        Enrollment.objects.create(
            user=self.student,
            course=self.course,
        )
        response = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/enrollments/")
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Students see only their own enrollments for the course
        self.assertEqual(response.data["count"], 1)

    @debug_on_failure
    def test_get_enrollments_for_student(self):
        self.client.force_authenticate(user=self.student)
        Enrollment.objects.create(
            user=self.student,
            course=self.course,
        )
        response = self.log_response(self.client.get("/api/enrollments/"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["course"]["id"], self.course.id
        )

    @debug_on_failure
    def test_get_enrollments_for_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        Enrollment.objects.create(
            user=self.student,
            course=self.course,
        )
        response = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/enrollments/")
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["user"]["id"], self.student.id
        )
