from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from elearning.models import Notification
from elearning.tests.test_base import BaseTestCase, debug_on_failure

User = get_user_model()


class NotificationViewSetTest(BaseTestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )

        # Create test notifications
        self.notification1 = Notification.objects.create(
            user=self.user1,
            title="Test Notification 1",
            message="This is a test notification",
            action_url="/test/url/1",
        )

        self.notification2 = Notification.objects.create(
            user=self.user1,
            title="Test Notification 2",
            message="This is another test notification",
            action_url="/test/url/2",
        )

        self.notification3 = Notification.objects.create(
            user=self.user2,
            title="Other User Notification",
            message="This notification belongs to another user",
            action_url="/test/url/3",
        )

        # URLs - Use hardcoded URLs like other tests
        self.list_url = "/api/notifications/"
        self.mark_read_url = (
            f"/api/notifications/{self.notification1.id}/mark_as_read/"
        )
        self.mark_all_read_url = "/api/notifications/mark_all_as_read/"

    @debug_on_failure
    def test_list_notifications_authenticated(self):
        """Test that authenticated users can list their own notifications"""
        self.client.force_authenticate(user=self.user1)
        response = self.log_response(self.client.get(self.list_url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # Should only show user1's notifications
        notification_ids = [n["id"] for n in response.data["results"]]
        self.assertIn(self.notification1.id, notification_ids)
        self.assertIn(self.notification2.id, notification_ids)
        self.assertNotIn(self.notification3.id, notification_ids)

    @debug_on_failure
    def test_mark_notification_as_read(self):
        """Test marking a single notification as read"""
        self.client.force_authenticate(user=self.user1)

        # Initially notification is unread
        self.assertFalse(self.notification1.is_read)

        response = self.log_response(self.client.patch(self.mark_read_url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"], "Notification marked as read"
        )
        self.assertTrue(response.data["is_read"])

        # Check database was updated
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    @debug_on_failure
    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read for a user"""
        self.client.force_authenticate(user=self.user1)

        # Initially both notifications are unread
        self.assertFalse(self.notification1.is_read)
        self.assertFalse(self.notification2.is_read)

        response = self.log_response(self.client.patch(self.mark_all_read_url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"], "2 notifications marked as read"
        )

        # Check database was updated
        self.notification1.refresh_from_db()
        self.notification2.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertTrue(self.notification2.is_read)

    @debug_on_failure
    def test_list_notifications_unauthenticated(self):
        """Test that unauthenticated users cannot list notifications"""
        response = self.log_response(self.client.get(self.list_url))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @debug_on_failure
    def test_mark_notification_read_unauthenticated(self):
        """Test that unauthenticated users cannot mark notifications as read"""
        response = self.log_response(self.client.patch(self.mark_read_url))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @debug_on_failure
    def test_mark_all_notifications_read_unauthenticated(self):
        """Test unauthenticated users cannot mark all notifications as read"""
        response = self.log_response(self.client.patch(self.mark_all_read_url))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @debug_on_failure
    def test_mark_other_user_notification_read(self):
        """Test that users cannot mark other users' notifications as read"""
        self.client.force_authenticate(user=self.user1)

        # Try to mark user2's notification as read
        other_user_mark_url = (
            f"/api/notifications/{self.notification3.id}/mark_as_read/"
        )
        response = self.log_response(self.client.patch(other_user_mark_url))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @debug_on_failure
    def test_mark_nonexistent_notification_read(self):
        """Test marking a non-existent notification as read"""
        self.client.force_authenticate(user=self.user1)

        nonexistent_url = "/api/notifications/99999/mark_as_read/"
        response = self.log_response(self.client.patch(nonexistent_url))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @debug_on_failure
    def test_notification_serializer_fields(self):
        """Test that notification serializer includes correct fields"""
        self.client.force_authenticate(user=self.user1)
        response = self.log_response(self.client.get(self.list_url))

        notification_data = response.data["results"][0]
        expected_fields = [
            "id",
            "title",
            "message",
            "action_url",
            "is_read",
            "created_at",
        ]

        for field in expected_fields:
            self.assertIn(field, notification_data)

    @debug_on_failure
    def test_mark_all_notifications_read_when_none_unread(self):
        """Test marking all notifications as read when none are unread"""
        self.client.force_authenticate(user=self.user1)

        # Mark all notifications as read first
        self.client.patch(self.mark_all_read_url)

        # Try to mark all as read again
        response = self.log_response(self.client.patch(self.mark_all_read_url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"], "0 notifications marked as read"
        )
