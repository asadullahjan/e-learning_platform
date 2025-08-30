from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from elearning.models import Course, Enrollment
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure

User = get_user_model()


class CourseEnrollmentViewsTest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.teacher = self._create_user("teacher", "teacher")
        self.student = self._create_user("student", "student")
        self.course = self._create_course(
            "Test Course", self.teacher, published=True
        )
        self.unpublished_course = self._create_course(
            "Unpublished", self.teacher, published=False
        )

    # ------------------- Helpers -------------------
    def _create_user(self, username, role):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="testpass",
            role=role,
        )

    def _create_course(self, title, teacher, published=True):
        return Course.objects.create(
            title=title,
            description="Course description",
            teacher=teacher,
            published_at=timezone.now() if published else None,
        )

    def _enroll_student(self, course, student):
        return Enrollment.objects.create(user=student, course=course)

    # ------------------- ENROLL -------------------
    @debug_on_failure
    def test_student_can_enroll_in_published_course(self):
        self.client.force_authenticate(user=self.student)
        resp = self.log_response(
            self.client.post(f"/api/courses/{self.course.id}/enrollments/", {})
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        enrollment = Enrollment.objects.get(id=resp.data["id"])
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.user, self.student)

    @debug_on_failure
    def test_student_cannot_enroll_in_unpublished_course(self):
        self.client.force_authenticate(user=self.student)
        resp = self.log_response(
            self.client.post(
                f"/api/courses/{self.unpublished_course.id}/enrollments/", {}
            )
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @debug_on_failure
    def test_unauthenticated_cannot_enroll(self):
        resp = self.log_response(
            self.client.post(f"/api/courses/{self.course.id}/enrollments/", {})
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------- LIST ENROLLMENTS -------------------
    @debug_on_failure
    def test_teacher_can_list_course_enrollments(self):
        self._enroll_student(self.course, self.student)
        self.client.force_authenticate(user=self.teacher)
        resp = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/enrollments/")
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(
            resp.data["results"][0]["user"]["id"], self.student.id
        )

    @debug_on_failure
    def test_student_can_list_own_enrollments(self):
        self._enroll_student(self.course, self.student)
        self.client.force_authenticate(user=self.student)
        resp = self.log_response(self.client.get("/api/enrollments/"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(
            resp.data["results"][0]["course"]["id"], self.course.id
        )
