from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from elearning.tests.test_base import BaseAPITestCase, debug_on_failure


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
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
            role="teacher",
            first_name="Jane",
            last_name="Smith",
        )
        self.client.force_authenticate(user=self.user)

        self.profile_url = "/api/users/me/"
        self.update_url = "/api/users/profile_update/"
        self.users_list_url = "/api/users/"
        self.other_user_url = f"/api/users/{self.other_user.username}/"

    @debug_on_failure
    def test_get_user_profile(self):
        """Test getting user profile"""
        response = self.log_response(self.client.get(self.profile_url))
        self.assertStatusCode(response, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["role"], "student")

    @debug_on_failure
    def test_update_user_profile(self):
        """Test updating user profile"""
        update_data = {"first_name": "Jane", "last_name": "Smith"}

        response = self.log_response(
            self.client.patch(self.update_url, update_data)
        )
        self.assertStatusCode(response, status.HTTP_200_OK)

        # Check user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jane")

    @debug_on_failure
    def test_unauthorized_profile_access(self):
        """Test profile access without authentication"""
        self.client.force_authenticate(user=None)

        response = self.log_response(self.client.get(self.profile_url))
        self.assertStatusCode(response, status.HTTP_401_UNAUTHORIZED)

    @debug_on_failure
    def test_any_user_can_view_all_users(self):
        """Test that any authenticated user can view all users"""
        response = self.log_response(self.client.get(self.users_list_url))
        self.assertStatusCode(response, status.HTTP_200_OK)

        # Should see both users
        self.assertEqual(len(response.data["results"]), 2)
        usernames = [user["username"] for user in response.data["results"]]
        self.assertIn("testuser", usernames)
        self.assertIn("otheruser", usernames)

    @debug_on_failure
    def test_any_user_can_view_other_user_profile(self):
        """
        Test that any authenticated user can view any other user's profile
        """
        response = self.log_response(self.client.get(self.other_user_url))
        self.assertStatusCode(response, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["username"], "otheruser")
        self.assertEqual(data["email"], "other@example.com")
        self.assertEqual(data["first_name"], "Jane")
        self.assertEqual(data["role"], "teacher")

    @debug_on_failure
    def test_user_search_functionality(self):
        """Test that users can search for other users"""
        # Search by username
        response = self.log_response(
            self.client.get(f"{self.users_list_url}?search=otheruser")
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], "otheruser")

        # Search by first name
        response = self.log_response(
            self.client.get(f"{self.users_list_url}?search=Jane")
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["first_name"], "Jane")

        # Search by last name
        response = self.log_response(
            self.client.get(f"{self.users_list_url}?search=Smith")
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["last_name"], "Smith")
