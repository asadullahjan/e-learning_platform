from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from elearning.tests.test_base import BaseAPITestCase


User = get_user_model()


class UserProfileTest(BaseAPITestCase):
    """Test user profile endpoints via UserViewSet"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
            first_name="John",
            last_name="Doe",
        )
        self.client.force_authenticate(user=self.user)

        self.profile_url = "/api/users/profile/"
        self.update_url = "/api/users/profile_update/"

    def test_get_user_profile(self):
        """Test getting user profile"""
        response = self.client.get(self.profile_url)
        self.assertStatusCode(response, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["role"], "student")

    def test_update_user_profile(self):
        """Test updating user profile"""
        update_data = {"first_name": "Jane", "last_name": "Smith"}

        response = self.client.patch(self.update_url, update_data)
        self.assertStatusCode(response, status.HTTP_200_OK)

        # Check user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jane")

    def test_unauthorized_profile_access(self):
        """Test profile access without authentication"""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.profile_url)
        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)
