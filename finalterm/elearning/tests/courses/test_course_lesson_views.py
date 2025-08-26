from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from elearning.models import Course, CourseLesson, Enrollment, User, File
from elearning.tests.test_base import BaseTestCase, debug_on_failure
from django.utils import timezone


class CourseLessonViewSetTestCase(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="teststudent",
            email="teststudent@example.com",
            password="testpassword",
            role="student",
        )

        self.client.force_authenticate(user=self.teacher)

        # Create a course
        description = "Test Description, adding more text to get 20 characters"
        self.course = Course.objects.create(
            title="Test Course",
            description=description,
            teacher=self.teacher,
            published_at=timezone.now(),
        )

        Enrollment.objects.create(user=self.student, course=self.course)

    @debug_on_failure
    def test_get_unpublished_course_lessons_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        CourseLesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
        )
        response = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/lessons/")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Lesson")

    @debug_on_failure
    def test_get_unpublished_course_lessons_as_student(self):
        self.client.force_authenticate(user=self.teacher)
        CourseLesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
        )

        self.client.force_authenticate(user=self.student)
        response = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/lessons/")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    @debug_on_failure
    def test_get_published_course_lessons_as_student(self):
        self.client.force_authenticate(user=self.teacher)
        CourseLesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
            published_at=timezone.now(),
        )

        self.client.force_authenticate(user=self.student)
        response = self.log_response(
            self.client.get(f"/api/courses/{self.course.id}/lessons/")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Lesson")

    @debug_on_failure
    def test_create_lesson_with_file(self):
        """Test creating a lesson via API with file upload"""
        # Create test file
        test_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"This is a test PDF content",
            content_type="application/pdf",
        )

        data = {
            "title": "Test Lesson",
            "description": "Test Lesson Description",
            "content": "Test Lesson Content",
            "file": test_file,
        }

        url = f"/api/courses/{self.course.id}/lessons/"
        response = self.log_response(
            self.client.post(url, data, format="multipart")
        )

        # Assert success
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert lesson was created with correct data
        lesson = CourseLesson.objects.get(title="Test Lesson")
        self.assertEqual(lesson.course, self.course)
        self.assertEqual(lesson.title, "Test Lesson")
        self.assertEqual(lesson.description, "Test Lesson Description")
        self.assertEqual(lesson.content, "Test Lesson Content")
        self.assertIsNotNone(lesson.file)
        self.assertIsNone(
            lesson.published_at
        )  # Should not be published initially
        self.assertIsNotNone(lesson.created_at)
        self.assertIsNotNone(lesson.updated_at)

        # Assert file was created with correct data
        self.assertEqual(lesson.file.original_name, "test_document.pdf")
        self.assertEqual(lesson.file.uploaded_by, self.teacher)
        self.assertTrue(
            lesson.file.is_previewable
        )  # PDF should be previewable
        self.assertEqual(lesson.file.mime_type, "application/pdf")

        # Assert relationships are correct
        self.assertIn(lesson, self.course.lessons.all())
        self.assertIn(lesson, lesson.file.lessons.all())
        self.assertEqual(lesson.file.uploaded_by, self.course.teacher)

    @debug_on_failure
    def test_create_lesson_without_file(self):
        """Test creating a lesson via API without file"""
        data = {
            "title": "Test Lesson No File",
            "description": "Test Description",
            "content": "Test Content",
        }

        url = f"/api/courses/{self.course.id}/lessons/"
        response = self.log_response(
            self.client.post(url, data, format="json")
        )

        # Assert success
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert lesson was created
        lesson = CourseLesson.objects.get(title="Test Lesson No File")
        self.assertEqual(lesson.course, self.course)
        self.assertIsNone(lesson.file)

    @debug_on_failure
    def test_create_lesson_unauthorized(self):
        """Test creating a lesson without authentication"""
        self.client.force_authenticate(user=None)

        data = {
            "title": "Test Lesson",
            "description": "Test Description",
            "content": "Test Content",
        }

        url = f"/api/courses/{self.course.id}/lessons/"
        response = self.log_response(
            self.client.post(url, data, format="json")
        )

        # Assert unauthorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_update_lesson(self):
        """Test updating a lesson via API"""
        # First create a lesson
        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Original Title",
            description="Original Description",
            content="Original Content",
        )

        # Update data
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "content": "Updated Content",
        }

        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/"
        response = self.log_response(
            self.client.patch(url, update_data, format="json")
        )

        # Assert success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert lesson was updated
        lesson.refresh_from_db()
        self.assertEqual(lesson.title, "Updated Title")
        self.assertEqual(lesson.description, "Updated Description")
        self.assertEqual(lesson.content, "Updated Content")

    @debug_on_failure
    def test_update_lesson_with_file(self):
        """Test updating a lesson with a new file"""
        # First create a lesson with a file
        test_file = SimpleUploadedFile(
            name="original.pdf",
            content=b"Original content",
            content_type="application/pdf",
        )

        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Original Title",
            description="Original Description",
            content="Original Content",
        )

        file_obj = File.objects.create(
            file=test_file,
            uploaded_by=self.teacher,
        )
        lesson.file = file_obj
        lesson.save()

        # Update with new file
        new_file = SimpleUploadedFile(
            name="new.pdf",
            content=b"New content",
            content_type="application/pdf",
        )

        update_data = {
            "title": "Updated Title",
            "file": new_file,
        }

        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/"
        response = self.log_response(
            self.client.patch(url, update_data, format="multipart")
        )

        # Assert success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert lesson was updated
        lesson.refresh_from_db()
        self.assertEqual(lesson.title, "Updated Title")
        self.assertEqual(lesson.file.original_name, "new.pdf")

    @debug_on_failure
    def test_delete_lesson(self):
        """Test deleting a lesson via API"""
        # First create a lesson
        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Lesson to Delete",
            description="Description",
            content="Content",
        )

        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/"
        response = self.log_response(self.client.delete(url))

        # Assert success
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert lesson was deleted
        self.assertFalse(CourseLesson.objects.filter(id=lesson.id).exists())

    @debug_on_failure
    def test_delete_lesson_with_file(self):
        """Test deleting a lesson that has a file"""
        # First create a lesson with a file
        test_file = SimpleUploadedFile(
            name="test.pdf",
            content=b"Test content",
            content_type="application/pdf",
        )

        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Lesson with File",
            description="Description",
            content="Content",
        )

        file_obj = File.objects.create(
            file=test_file,
            uploaded_by=self.teacher,
        )
        lesson.file = file_obj
        lesson.save()

        # Delete the lesson
        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/"
        response = self.log_response(self.client.delete(url))

        # Assert success
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert lesson and file were deleted
        self.assertFalse(CourseLesson.objects.filter(id=lesson.id).exists())
        self.assertFalse(File.objects.filter(id=file_obj.id).exists())

    @debug_on_failure
    def test_download_lesson_file(self):
        """Test downloading a lesson file"""
        # Create lesson with file
        test_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"This is a test PDF content",
            content_type="application/pdf",
        )

        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
        )

        file_obj = File.objects.create(
            file=test_file,
            uploaded_by=self.teacher,
        )
        lesson.file = file_obj
        lesson.save()

        # Test download as teacher
        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
        response = self.log_response(self.client.get(url))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/octet-stream")
        self.assertIn("attachment", response["Content-Disposition"])

    @debug_on_failure
    def test_download_lesson_file_as_student(self):
        """Test downloading a lesson file as enrolled student"""
        # Create lesson with file
        test_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"This is a test PDF content",
            content_type="application/pdf",
        )

        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
            published_at=timezone.now(),  # Must be published for students
        )

        file_obj = File.objects.create(
            file=test_file,
            uploaded_by=self.teacher,
        )
        lesson.file = file_obj
        lesson.save()

        # Test download as enrolled student
        self.client.force_authenticate(user=self.student)
        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
        response = self.log_response(self.client.get(url))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/octet-stream")

    @debug_on_failure
    def test_download_lesson_file_unauthorized(self):
        """Test downloading a lesson file without permission"""
        # Create lesson with file
        test_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"This is a test PDF content",
            content_type="application/pdf",
        )

        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
        )

        file_obj = File.objects.create(
            file=test_file,
            uploaded_by=self.teacher,
        )
        lesson.file = file_obj
        lesson.save()

        # Test download without authentication
        self.client.force_authenticate(user=None)
        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
        response = self.log_response(self.client.get(url))

        self.assertEqual(response.status_code, 403)

    @debug_on_failure
    def test_download_lesson_file_no_file(self):
        """Test downloading a lesson that has no file"""
        # Create lesson without file
        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
        )

        # Test download attempt
        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
        response = self.log_response(self.client.get(url))

        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "No file available for download", response.data["detail"]
        )

    @debug_on_failure
    def test_download_lesson_file_student_not_enrolled(self):
        """Test downloading a lesson file as non-enrolled student"""
        # Create another student who is not enrolled
        non_enrolled_student = User.objects.create_user(
            username="nonenrolled",
            email="nonenrolled@example.com",
            password="testpassword",
            role="student",
        )

        # Create lesson with file
        test_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"This is a test PDF content",
            content_type="application/pdf",
        )

        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
            published_at=timezone.now(),
        )

        file_obj = File.objects.create(
            file=test_file,
            uploaded_by=self.teacher,
        )
        lesson.file = file_obj
        lesson.save()

        # Test download as non-enrolled student
        self.client.force_authenticate(user=non_enrolled_student)
        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/download/"
        response = self.log_response(self.client.get(url))

        self.assertEqual(response.status_code, 403)
        self.assertIn("permission_denied", response.data["detail"].code)

    @debug_on_failure
    def test_publish_lesson(self):
        """Test publishing a lesson via partial update"""
        # First create a lesson
        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Draft Lesson",
            description="Description",
            content="Content",
        )

        # Publish the lesson
        publish_data = {
            "published_at": timezone.now().isoformat(),
        }

        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/"
        response = self.log_response(
            self.client.patch(url, publish_data, format="json")
        )

        # Assert success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert lesson was published
        lesson.refresh_from_db()
        self.assertIsNotNone(lesson.published_at)

    @debug_on_failure
    def test_unpublish_lesson(self):
        """Test unpublishing a lesson via partial update"""
        # First create a published lesson
        lesson = CourseLesson.objects.create(
            course=self.course,
            title="Published Lesson",
            description="Description",
            content="Content",
            published_at=timezone.now(),
        )

        # Unpublish the lesson
        unpublish_data = {
            "published_at": None,
        }

        url = f"/api/courses/{self.course.id}/lessons/{lesson.id}/"
        response = self.log_response(
            self.client.patch(url, unpublish_data, format="json")
        )

        # Assert success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert lesson was unpublished
        lesson.refresh_from_db()
        self.assertIsNone(lesson.published_at)
