from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from elearning.models import User, Course, StudentRestriction, Enrollment
from elearning.tests.test_base import BaseTestCase, debug_on_failure


@patch(
    "elearning.services.notification_service.NotificationService"
    "._send_websocket_message"
)
class StudentRestrictionViewsTestCase(BaseTestCase):
    """
    Test case for student restriction views.
    """

    def setUp(self, mock_notification=None):
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
        from django.utils import timezone

        self.course1 = Course.objects.create(
            title="Test Course 1",
            description=course_description,
            teacher=self.teacher1,
            published_at=timezone.now(),  # Publish the course
        )

        self.course2 = Course.objects.create(
            title="Test Course 2",
            description=course_description,
            teacher=self.teacher1,
            published_at=timezone.now(),  # Publish the course
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
    def test_get_restrictions_list_student(self, mock_notification):
        """Test that students cannot access restrictions list."""
        self.client.force_authenticate(user=self.student1)
        response = self.log_response(
            self.client.get(self.restrictions_list_url)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_get_restrictions_list_teacher(self, mock_notification):
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
    def test_get_restrictions_list_other_teacher(self, mock_notification):
        """Test that teachers only see their own restrictions."""
        self.client.force_authenticate(user=self.teacher2)
        response = self.log_response(
            self.client.get(self.restrictions_list_url)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    @debug_on_failure
    def test_create_restriction_unauthorized_scenarios(
        self, mock_notification
    ):
        """Test various unauthorized creation scenarios."""
        data = {
            "student_id": self.student2.id,
            "course_id": self.course1.id,
            "reason": "Test restriction",
        }

        # Test 1: Unauthenticated users cannot create restrictions
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test 2: Students cannot create restrictions
        self.client.force_authenticate(user=self.student1)
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_create_restriction_teacher_success(self, mock_notification):
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
    def test_create_restriction_duplicate(self, mock_notification):
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
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("already restricted", response.data["detail"])

    @debug_on_failure
    def test_create_restriction_invalid_scenarios(self, mock_notification):
        """Test creation with invalid data scenarios."""
        self.client.force_authenticate(user=self.teacher1)

        # Test 1: Teachers cannot restrict other teachers
        data = {
            "student_id": self.teacher2.id,
            "course_id": self.course1.id,
            "reason": "Restrict teacher",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("only be applied to students", response.data["detail"])

        # Test 2: Teachers cannot restrict students in other teachers' courses
        other_teacher_course = Course.objects.create(
            title="Other Teacher Course",
            description=(
                "Test Description, adding more text to get 20 characters"
            ),
            teacher=self.teacher2,
        )
        data = {
            "student_id": self.student2.id,
            "course_id": other_teacher_course.id,
            "reason": "Cross-course restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_delete_restriction_owner(self, mock_notification):
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
        # Refresh from database to get updated state after signal processing
        enrollment.refresh_from_db()
        self.assertTrue(enrollment.is_active)

    @debug_on_failure
    def test_delete_restriction_non_owner(self, mock_notification):
        """Test that non-owners cannot delete restrictions."""
        self.client.force_authenticate(user=self.teacher2)
        response = self.log_response(
            self.client.delete(self.restriction_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify restriction still exists (wasn't actually deleted)
        self.assertEqual(StudentRestriction.objects.count(), 1)

    @debug_on_failure
    def test_check_student_restriction_scenarios(self, mock_notification):
        """Test various student restriction checking scenarios."""
        self.client.force_authenticate(user=self.teacher1)

        # Test 1: Student with course-specific restriction
        response = self.log_response(
            self.client.get(
                self.check_student_url,
                {"student_id": self.student1.id, "course_id": self.course1.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_restricted"])

        # Test 2: Student without restriction
        response = self.log_response(
            self.client.get(
                self.check_student_url,
                {"student_id": self.student2.id, "course_id": self.course1.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_restricted"])

        # Test 3: Create teacher all-courses restriction and verify it affects
        # all courses
        StudentRestriction.objects.create(
            teacher=self.teacher1,
            student=self.student2,
            course=None,  # All courses by this teacher
            reason="Banned from all my courses",
        )

        # Test student2 is now restricted from course1
        response = self.log_response(
            self.client.get(
                self.check_student_url,
                {"student_id": self.student2.id, "course_id": self.course1.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_restricted"])

        # Test student2 is also restricted from course2 (same teacher)
        response = self.log_response(
            self.client.get(
                self.check_student_url,
                {"student_id": self.student2.id, "course_id": self.course2.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_restricted"])

    @debug_on_failure
    def test_retrieve_restriction_access_scenarios(self, mock_notification):
        """Test various restriction retrieval access scenarios."""
        # Test 1: Teachers can retrieve their own restrictions
        self.client.force_authenticate(user=self.teacher1)
        response = self.log_response(
            self.client.get(self.restriction_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.restriction1.pk)

        # Test 2: Affected students can view restrictions applied to them
        self.client.force_authenticate(user=self.student1)
        response = self.log_response(
            self.client.get(self.restriction_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.restriction1.pk)

        # Test 3: Non-affected student cannot view restriction
        self.client.force_authenticate(user=self.student2)
        response = self.log_response(
            self.client.get(self.restriction_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test 4: Other teacher cannot view restriction
        self.client.force_authenticate(user=self.teacher2)
        response = self.log_response(
            self.client.get(self.restriction_detail_url)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @debug_on_failure
    def test_check_student_missing_parameters(self, mock_notification):
        """Test check_student endpoint with missing parameters."""
        self.client.force_authenticate(user=self.teacher1)

        # Test without student_id
        response = self.log_response(
            self.client.get(
                self.check_student_url, {"course_id": self.course1.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("student_id is required", response.data["detail"])

    @debug_on_failure
    def test_create_teacher_all_courses_restriction(self, mock_notification):
        """Test creating a teacher all-courses restriction (no course)."""
        self.client.force_authenticate(user=self.teacher1)
        data = {
            "student_id": self.student2.id,
            "reason": "Restricted from all my courses",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify it's a teacher all-courses restriction
        restriction = StudentRestriction.objects.get(
            student=self.student2, teacher=self.teacher1, course__isnull=True
        )
        self.assertIsNone(restriction.course)
        self.assertEqual(restriction.teacher, self.teacher1)

    @debug_on_failure
    def test_restriction_integration_course_access_behavior(
        self, mock_notification
    ):
        """Test that restrictions allow course info access but block content."""
        from elearning.services.courses.course_service import CourseService
        from elearning.services.courses.course_lesson_service import (
            CourseLessonService,
        )
        from elearning.exceptions import ServiceError

        # Test 1: Restricted student CAN access course general information
        # (This is the correct behavior - they can see course details)
        try:
            course = CourseService.get_course_with_permission_check(
                self.course1.id, self.student1
            )
            self.assertEqual(course.id, self.course1.id)
        except ServiceError:
            self.fail(
                "Restricted student should be able to access course general info"
            )

        # Test 2: Restricted student CANNOT access lesson content
        # Create a lesson for testing
        from elearning.models import CourseLesson
        from django.utils import timezone

        lesson = CourseLesson.objects.create(
            course=self.course1,
            title="Test Lesson",
            description="Test Description",
            content="Test Content",
            published_at=timezone.now(),
        )

        # Restricted student should not be able to view lesson content
        with self.assertRaises(ServiceError) as context:
            CourseLessonService.get_lesson_with_permission_check(
                lesson.id, self.student1
            )
        self.assertIn("permission", str(context.exception).lower())

        # Test 3: Non-restricted student can access both course and lessons
        try:
            course = CourseService.get_course_with_permission_check(
                self.course1.id, self.student2
            )
            self.assertEqual(course.id, self.course1.id)
        except ServiceError:
            self.fail("Student2 should be able to access course1")

        # Test 4: Create teacher all-courses restriction and verify behavior
        StudentRestriction.objects.create(
            teacher=self.teacher1,
            student=self.student2,
            course=None,
            reason="Banned from all my courses",
        )

        # Student2 should still be able to access course general info
        try:
            course = CourseService.get_course_with_permission_check(
                self.course1.id, self.student2
            )
            self.assertEqual(course.id, self.course1.id)
        except ServiceError:
            self.fail(
                "Student2 should still be able to access course general info"
            )

        # But student2 should not be able to access lesson content
        with self.assertRaises(ServiceError):
            CourseLessonService.get_lesson_with_permission_check(
                lesson.id, self.student2
            )

    @debug_on_failure
    def test_restriction_lesson_list_access_behavior(self, mock_notification):
        """Test that restricted students can see lesson lists but not content."""
        from elearning.services.courses.course_lesson_service import (
            CourseLessonService,
        )
        from elearning.models import CourseLesson
        from django.utils import timezone

        # Create lessons for testing
        lesson1 = CourseLesson.objects.create(
            course=self.course1,
            title="Published Lesson",
            description="Test Description",
            content="Test Content",
            published_at=timezone.now(),
        )

        # lesson2 = CourseLesson.objects.create(
        #     course=self.course1,
        #     title="Unpublished Lesson",
        #     description="Test Description",
        #     content="Test Content",
        #     # Not published
        # )

        # Test 1: Restricted student should see NO lessons in lesson list
        # (because they're not enrolled - enrollment.is_active = False)
        lessons = CourseLessonService.get_lessons_for_course(
            self.course1, self.student1
        )
        self.assertEqual(lessons.count(), 0)

        # create enrollment for student2
        Enrollment.objects.create(
            course=self.course1, user=self.student2, is_active=True
        )

        # Test 2: Non-restricted student should see published lessons
        lessons = CourseLessonService.get_lessons_for_course(
            self.course1, self.student2
        )
        self.assertEqual(lessons.count(), 1)
        self.assertEqual(lessons.first().id, lesson1.id)

    @debug_on_failure
    def test_restriction_feedback_access_behavior(self, mock_notification):
        """Test that restricted students can still view feedbacks."""
        from elearning.models import CourseFeedback
        from elearning.services.courses.course_feedback_service import (
            CourseFeedbackService,
        )

        # Create feedback from another student
        other_student = User.objects.create_user(
            username="other_student",
            email="other@test.com",
            password="testpass123",
            role="student",
        )

        # Enroll other student in course1
        Enrollment.objects.create(
            course=self.course1, user=other_student, is_active=True
        )

        # Create feedback
        feedback = CourseFeedback.objects.create(
            course=self.course1,
            user=other_student,
            rating=5,
            text="This is a great course with more than 10 characters",
        )

        # Test 1: Restricted student CAN view feedbacks
        # (This is the correct behavior - feedbacks are public)
        try:
            feedback_obj = (
                CourseFeedbackService.get_feedback_with_permission_check(
                    feedback.id, self.student1
                )
            )
            self.assertEqual(feedback_obj.id, feedback.id)
        except Exception as e:
            self.fail(
                f"Restricted student should be able to view feedbacks: {e}"
            )

        # Test 2: Restricted student CANNOT create feedback
        # (because they're not enrolled - enrollment.is_active = False)
        from elearning.permissions.courses.feedback_permissions import (
            CourseFeedbackPolicy,
        )

        can_leave_feedback = CourseFeedbackPolicy.check_can_leave_feedback(
            self.student1, self.course1, raise_exception=False
        )
        self.assertFalse(can_leave_feedback)

        # create enrollment for student2
        Enrollment.objects.create(
            course=self.course1, user=self.student2, is_active=True
        )

        # Test 3: Non-restricted student CAN create feedback
        can_leave_feedback = CourseFeedbackPolicy.check_can_leave_feedback(
            self.student2, self.course1, raise_exception=True
        )
        self.assertTrue(can_leave_feedback)

    @debug_on_failure
    def test_restriction_enrollment_reactivation_blocking(
        self, mock_notification
    ):
        """Test that restricted students cannot reactivate enrollments."""
        from elearning.services.courses.enrollment_service import (
            EnrollmentService,
        )
        from elearning.exceptions import ServiceError

        # Test 1: Restricted student cannot reactivate enrollment
        with self.assertRaises(ServiceError) as context:
            EnrollmentService.enroll_student(self.course1, self.student1)
        self.assertIn("restricted", str(context.exception).lower())

        # Test 2: Non-restricted student can enroll/reactivate
        try:
            enrollment = EnrollmentService.enroll_student(
                self.course1, self.student2
            )
            self.assertTrue(enrollment.is_active)
        except ServiceError:
            self.fail("Non-restricted student should be able to enroll")

        # Test 3: Create restriction and try to reactivate
        StudentRestriction.objects.create(
            teacher=self.teacher1,
            student=self.student2,
            course=self.course1,
            reason="Now restricted",
        )

        # Deactivate the enrollment (simulate restriction effect)
        enrollment.is_active = False
        enrollment.save()

        # Now student2 should not be able to reactivate
        with self.assertRaises(ServiceError) as context:
            EnrollmentService.enroll_student(self.course1, self.student2)
        self.assertIn("restricted", str(context.exception).lower())

    @debug_on_failure
    def test_restriction_integration_course_listing_filtering(
        self, mock_notification
    ):
        """Test that restrictions filter courses from listing."""
        from elearning.services.courses.course_service import CourseService

        # Publish courses so they appear in listings
        self.course1.published_at = "2023-01-01T00:00:00Z"
        self.course1.save()
        self.course2.published_at = "2023-01-01T00:00:00Z"
        self.course2.save()

        # Test 1: Student1 (restricted from course1) should only see course2
        courses = CourseService.get_courses_for_user(self.student1)
        course_ids = list(courses.values_list("id", flat=True))
        self.assertNotIn(self.course1.id, course_ids)
        self.assertIn(self.course2.id, course_ids)

        # Test 2: Student2 (not restricted) should see both courses
        courses = CourseService.get_courses_for_user(self.student2)
        course_ids = list(courses.values_list("id", flat=True))
        self.assertIn(self.course1.id, course_ids)
        self.assertIn(self.course2.id, course_ids)

        # Test 3: Create teacher all-courses restriction
        StudentRestriction.objects.create(
            teacher=self.teacher1,
            student=self.student2,
            course=None,
            reason="Banned from all my courses",
        )

        # Now student2 should see neither course
        courses = CourseService.get_courses_for_user(self.student2)
        course_ids = list(courses.values_list("id", flat=True))
        self.assertNotIn(self.course1.id, course_ids)
        self.assertNotIn(self.course2.id, course_ids)

    @debug_on_failure
    def test_overlapping_restrictions_prevention(self, mock_notification):
        """Test that overlapping restrictions are prevented."""
        self.client.force_authenticate(user=self.teacher1)
        
        # Test 1: Create global restriction first
        data = {
            "student_id": self.student2.id,
            "reason": "Global restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test 2: Try to create individual course restriction - should fail
        data = {
            "student_id": self.student2.id,
            "course_id": self.course1.id,
            "reason": "Individual restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("global restriction", response.data["detail"])
        
        # Test 3: Delete global restriction
        global_restriction = StudentRestriction.objects.get(
            student=self.student2, teacher=self.teacher1, course__isnull=True
        )
        delete_url = reverse(
            "elearning:restriction-detail", kwargs={"pk": global_restriction.pk}
        )
        response = self.log_response(
            self.client.delete(delete_url)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Test 4: Now should be able to create individual restriction
        data = {
            "student_id": self.student2.id,
            "course_id": self.course1.id,
            "reason": "Individual restriction",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test 5: Try to create global restriction again - should succeed and delete individual
        data = {
            "student_id": self.student2.id,
            "reason": "Global restriction again",
        }
        response = self.log_response(
            self.client.post(self.restrictions_list_url, data)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that the individual restriction was deleted and global was created
        individual_restrictions = StudentRestriction.objects.filter(
            student=self.student2, teacher=self.teacher1, course__isnull=False
        ).count()
        global_restrictions = StudentRestriction.objects.filter(
            student=self.student2, teacher=self.teacher1, course__isnull=True
        ).count()
        
        self.assertEqual(individual_restrictions, 0)  # Individual should be deleted
        self.assertEqual(global_restrictions, 1)      # Global should exist
