from django.contrib.auth import get_user_model
from elearning.tests.test_base import BaseTestCase, debug_on_failure

User = get_user_model()


class UserModelTest(BaseTestCase):
    """Test User model"""

    @debug_on_failure
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "student")
        self.assertTrue(user.is_active)

    @debug_on_failure
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="teacher",
        )
        expected_str = "testuser (Teacher)"
        self.assertEqual(str(user), expected_str)

    @debug_on_failure
    def test_user_role_choices(self):
        """Test user role choices"""
        student = User.objects.create_user(
            username="teststudent",
            email="student@example.com",
            password="testpass123",
            role="student",
        )

        teacher = User.objects.create_user(
            username="testteacher",
            email="teacher@example.com",
            password="testpass123",
            role="teacher",
        )

        self.assertEqual(student.get_role_display(), "Student")
        self.assertEqual(teacher.get_role_display(), "Teacher")
