from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from elearning.models import Status, User
from .test_base import BaseTestCase, BaseAPITestCase, debug_on_failure
from django.utils import timezone
from datetime import timedelta


class StatusModelTest(BaseTestCase):
    """Test the Status model"""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
        )

    @debug_on_failure
    def test_status_creation(self):
        """Test creating a status update"""
        status_obj = Status.objects.create(
            user=self.user, content="This is a test status update"
        )

        self.assertEqual(status_obj.user, self.user)
        self.assertEqual(status_obj.content, "This is a test status update")
        self.assertIsNotNone(status_obj.created_at)
        self.assertIsNotNone(status_obj.updated_at)


class StatusViewSetTest(BaseAPITestCase):
    """Test the StatusViewSet core functionality"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
            role="student",
        )
        self.status = Status.objects.create(
            user=self.user, content="Test status content"
        )
        self.other_status = Status.objects.create(
            user=self.other_user, content="Other user status"
        )

    @debug_on_failure
    def test_list_statuses_authenticated(self):
        """Test that authenticated users can list all statuses"""
        self.client.force_authenticate(user=self.user)
        url = reverse("elearning:status-list")
        response = self.log_response(self.client.get(url))

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    @debug_on_failure
    def test_list_statuses_unauthenticated(self):
        """Test that unauthenticated users cannot list statuses"""
        url = reverse("elearning:status-list")
        response = self.log_response(self.client.get(url))

        self.assertStatusCode(response, status.HTTP_401_UNAUTHORIZED)

    @debug_on_failure
    def test_create_status_authenticated(self):
        """Test that authenticated users can create statuses"""
        self.client.force_authenticate(user=self.user)
        url = reverse("elearning:status-list")
        data = {"content": "New status update"}

        response = self.log_response(self.client.post(url, data))
        self.assertStatusCode(response, status.HTTP_201_CREATED)
        self.assertEqual(Status.objects.count(), 3)

    @debug_on_failure
    def test_update_own_status(self):
        """Test that users can update their own statuses"""
        self.client.force_authenticate(user=self.user)
        url = reverse("elearning:status-detail", args=[self.status.id])
        data = {"content": "Updated content"}

        response = self.log_response(self.client.patch(url, data))

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.status.refresh_from_db()
        self.assertEqual(self.status.content, "Updated content")

    @debug_on_failure
    def test_update_other_user_status(self):
        """Test that users cannot update other users' statuses"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("elearning:status-detail", args=[self.status.id])
        data = {"content": "Updated content"}

        response = self.log_response(self.client.patch(url, data))

        self.assertStatusCode(response, status.HTTP_403_FORBIDDEN)

    @debug_on_failure
    def test_delete_own_status(self):
        """Test that users can delete their own statuses"""
        self.client.force_authenticate(user=self.user)
        url = reverse("elearning:status-detail", args=[self.status.id])

        response = self.log_response(self.client.delete(url))

        self.assertStatusCode(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Status.objects.count(), 1)


class StatusFilterTest(BaseAPITestCase):
    """Test the StatusFilter functionality"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="student",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
            role="teacher",
        )

        # Create statuses with different content and users
        self.status1 = Status.objects.create(
            user=self.user, content="Hello world status"
        )
        self.status2 = Status.objects.create(
            user=self.other_user, content="Another status message"
        )
        self.status3 = Status.objects.create(
            user=self.user, content="Test status for filtering"
        )

        self.client.force_authenticate(user=self.user)

    @debug_on_failure
    def test_filter_by_user_id(self):
        """Test filtering statuses by user ID"""
        url = reverse("elearning:status-list")
        response = self.log_response(
            self.client.get(f"{url}?user={self.user.id}")
        )

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        for result in response.data["results"]:
            self.assertEqual(result["user"]["username"], self.user.username)

    @debug_on_failure
    def test_search_by_username(self):
        """Test searching statuses by username"""
        url = reverse("elearning:status-list")
        response = self.log_response(
            self.client.get(f"{url}?search=otheruser")
        )

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["user"]["username"], "otheruser"
        )

    @debug_on_failure
    def test_filter_by_date_range(self):
        """Test filtering statuses by date range"""
        # Create a status with specific date (2 days ago)
        old_date = timezone.now() - timedelta(days=2)
        old_status = Status.objects.create(
            user=self.user, content="Old status"
        )
        old_status.created_at = old_date
        old_status.save(update_fields=["created_at"])

        url = reverse("elearning:status-list")

        # Filter by created_before
        filter_date = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.log_response(
            self.client.get(f"{url}?created_before={filter_date}")
        )
        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["content"], "Old status")

    @debug_on_failure
    def test_combine_filters(self):
        """Test combining multiple filters"""
        url = reverse("elearning:status-list")
        response = self.log_response(
            self.client.get(f"{url}?user={self.user.id}&search=status")
        )

        self.assertStatusCode(response, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
