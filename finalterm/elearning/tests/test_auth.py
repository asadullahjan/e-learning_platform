from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


class AuthenticationTest(APITestCase):
    """Test authentication endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"

        self.valid_payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "role": "student",
        }

    def test_user_registration(self):
        """Test user registration endpoint"""   
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)

        # Check user was created
        user = User.objects.get(email="test@example.com")
        self.assertEqual(user.role, "student")

    def test_user_login(self):
        """Test user login endpoint"""
        # Create user first
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
        )

        login_data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)

    def test_invalid_registration_data(self):
        """Test registration with invalid data"""
        invalid_payload = {
            "username": "te",  # Too short
            "email": "invalid-email",
            "password": "123",  # Too short
            "role": "invalid-role",
        }

        response = self.client.post(self.register_url, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_username_registration(self):
        """Test registration with duplicate username"""
        # Create first user
        User.objects.create_user(
            username="testuser",
            email="test1@example.com",
            password="testpass123",
            role="student",
        )

        # Try to register with same username
        duplicate_payload = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpass123",
            "role": "student",
        }

        response = self.client.post(self.register_url, duplicate_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
