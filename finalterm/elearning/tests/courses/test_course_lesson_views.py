from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from elearning.models import Course, CourseLesson, Enrollment, User, File
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure
from django.utils import timezone


class CourseLessonViewSetTestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.teacher = User.objects.create_user(
            username="teacher",
            email="teacher@example.com",
            password="testpass",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="testpass",
            role="student",
        )
        self.client.force_authenticate(user=self.teacher)

        self.course = Course.objects.create(
            title="Test Course",
            description="Course description long enough",
            teacher=self.teacher,
            published_at=timezone.now(),
        )
        Enrollment.objects.create(user=self.student, course=self.course)

    # -------------------
    # GET LESSONS
    # -------------------
    @debug_on_failure
    def test_teacher_sees_all_lessons(self):
        CourseLesson.objects.create(
            course=self.course, title="Draft", description="x", content="x"
        )
        CourseLesson.objects.create(
            course=self.course,
            title="Published",
            description="x",
            content="x",
            published_at=timezone.now(),
        )

        self.client.force_authenticate(user=self.teacher)
        resp = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/lessons/")
        )
        self.assertEqual(len(resp.data["results"]), 2)

    @debug_on_failure
    def test_student_sees_only_published_lessons(self):
        CourseLesson.objects.create(
            course=self.course, title="Draft", description="x", content="x"
        )
        CourseLesson.objects.create(
            course=self.course,
            title="Published",
            description="x",
            content="x",
            published_at=timezone.now(),
        )

        self.client.force_authenticate(user=self.student)
        resp = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/lessons/")
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)
        self.assertEqual(resp.data["results"][0]["title"], "Published")

    @debug_on_failure
    def test_student_cannot_see_lessons_in_unpublished_course(self):
        unpublished = Course.objects.create(
            title="Hidden", description="desc", teacher=self.teacher
        )
        Enrollment.objects.create(user=self.student, course=unpublished)
        CourseLesson.objects.create(
            course=unpublished,
            title="Lesson",
            description="x",
            content="x",
            published_at=timezone.now(),
        )

        self.client.force_authenticate(user=self.student)
        resp = self.log_response(
            self.client.get(f"/api/courses/{unpublished.id}/lessons/")
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------
    # CREATE
    # -------------------
    @debug_on_failure
    def test_teacher_can_create_lesson_with_file(self):
        file = SimpleUploadedFile(
            "doc.pdf", b"filecontent", content_type="application/pdf"
        )
        resp = self.log_response(
            self.client.post(
                f"/api/courses/{self.course.id}/lessons/",
                {
                    "title": "Lesson",
                    "description": "desc",
                    "content": "Test Content",
                    "file": file,
                },
                format="multipart",
            )
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CourseLesson.objects.filter(title="Lesson").exists())

    @debug_on_failure
    def test_student_cannot_create_lesson(self):
        self.client.force_authenticate(user=self.student)
        resp = self.log_response(
            self.client.post(
                f"/api/courses/{self.course.id}/lessons/",
                {"title": "x", "description": "x", "content": "x"},
            )
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------
    # UPDATE / PUBLISH
    # -------------------
    @debug_on_failure
    def test_teacher_can_update_and_publish(self):
        lesson = CourseLesson.objects.create(
            course=self.course, title="Draft", description="x", content="x"
        )

        resp = self.log_response(
            self.client.patch(
                f"/api/courses/{self.course.id}/lessons/{lesson.id}/",
                {
                    "title": "Updated",
                    "published_at": timezone.now().isoformat(),
                },
            )
        )
        lesson.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.title, "Updated")
        self.assertIsNotNone(lesson.published_at)

    # -------------------
    # DELETE
    # -------------------
    @debug_on_failure
    def test_teacher_can_delete_lesson(self):
        lesson = CourseLesson.objects.create(
            course=self.course, title="DeleteMe", description="x", content="x"
        )
        resp = self.log_response(
            self.client.delete(
                f"/api/courses/{self.course.id}/lessons/{lesson.id}/"
            )
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseLesson.objects.filter(id=lesson.id).exists())

    # -------------------
    # DOWNLOAD
    # -------------------
    @debug_on_failure
    def test_file_download_by_teacher_and_student(self):
        file = SimpleUploadedFile(
            "doc.pdf", b"filecontent", content_type="application/pdf"
        )
        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Lesson",
            description="x",
            content="x",
            published_at=timezone.now(),
        )
        lesson.file = File.objects.create(file=file, uploaded_by=self.teacher)
        lesson.save()

        # teacher
        resp_teacher = self.log_response(
            self.client.get(
                f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
            )
        )
        self.assertEqual(resp_teacher.status_code, status.HTTP_200_OK)

        # student
        self.client.force_authenticate(user=self.student)
        resp_student = self.log_response(
            self.client.get(
                f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
            )
        )
        self.assertEqual(resp_student.status_code, status.HTTP_200_OK)

    @debug_on_failure
    def test_download_fails_if_not_enrolled_or_no_file(self):
        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Lesson",
            description="x",
            content="x",
            published_at=timezone.now(),
        )

        # no file
        resp = self.log_response(
            self.client.get(
                f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
            )
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # non-enrolled user
        outsider = User.objects.create_user(
            "outsider", "o@example.com", "pass", role="student"
        )
        lesson.file = File.objects.create(
            file=SimpleUploadedFile(
                "doc.pdf", b"x", content_type="application/pdf"
            ),
            uploaded_by=self.teacher,
        )
        lesson.save()

        self.client.force_authenticate(user=outsider)
        resp = self.log_response(
            self.client.get(
                f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
            )
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
