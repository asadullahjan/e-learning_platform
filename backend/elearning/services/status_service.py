from django.db import transaction
from elearning.models import Status, User
from elearning.exceptions import ServiceError
from elearning.services.notification_service import NotificationService
from elearning.permissions import StatusPolicy


class StatusService:
    """
    Service for managing status operations and business logic.

    This service encapsulates all business logic related to status updates
    including:
    - Status creation and validation
    - Status modification and deletion
    - Permission checking for status operations

    The service follows the single responsibility principle and provides
    a clean interface for views to interact with status-related operations.
    All business rules are centralized here to ensure consistency.
    """

    @staticmethod
    @transaction.atomic
    def create_status(user: User, content: str) -> Status:
        """
        Create a new status and notify followers.

        This method creates status after validating all business rules.
        It ensures data integrity and provides meaningful error messages
        when validation fails.

        Args:
            user: User creating the status
            content: Status content text

        Returns:
            Status instance

        Raises:
            ServiceError: If validation fails (user not authenticated)

        Example:
            >>> status = StatusService.create_status(user, "Hello world!")
            >>> print(f"Created status: {status.content}")
        """
        # Use the permission policy for validation
        StatusPolicy.check_can_create_status(user, raise_exception=True)

        status = Status.objects.create(user=user, content=content)

        # Notify followers about new status
        # Note: This assumes you have a follow system
        # If not, you can implement it or remove this notification
        try:
            # Get users who follow this user (if follow system exists)
            followers = User.objects.filter(following=user)
            if followers.exists():
                NotificationService.create_notifications_and_send(
                    user_ids=[follower.id for follower in followers],
                    title="New Status Update",
                    message=f"{user.username} posted a new status",
                    action_url=f"/users/{user.username}",
                )
        except Exception:
            # If follow system doesn't exist, skip notification
            pass

        return status

    @staticmethod
    def get_status_with_permission_check(status_id: int, user: User) -> Status:
        """
        Get status with permission check.

        Args:
            status_id: ID of the status to retrieve
            user: User attempting to view the status

        Returns:
            Status instance

        Raises:
            ServiceError: If status not found or permission denied
        """
        try:
            status = Status.objects.get(id=status_id)
            # Check if user can view this status
            StatusPolicy.check_can_view_status(
                user, status, raise_exception=True
            )
            return status
        except Status.DoesNotExist:
            raise ServiceError.not_found("Status not found")

    @staticmethod
    @transaction.atomic
    def update_status(status: Status, user: User, content: str) -> Status:
        """
        Update status with permission check.

        This method allows users to modify their own status while
        ensuring only the status owner can make changes.

        Args:
            status: Status instance to update
            user: User making the update
            content: New content for the status

        Returns:
            Updated Status instance

        Raises:
            ServiceError: If user doesn't own the status
        """
        # Check if user can modify this status
        StatusPolicy.check_can_modify_status(
            user, status, raise_exception=True
        )

        status.content = content
        status.save()
        return status

    @staticmethod
    @transaction.atomic
    def delete_status(status: Status, user: User):
        """
        Delete status with permission check.

        This method allows users to delete their own status while
        ensuring only the status owner can perform deletion.

        Args:
            status: Status instance to delete
            user: User attempting to delete the status

        Raises:
            ServiceError: If user doesn't own the status
        """
        # Check if user can delete this status
        StatusPolicy.check_can_delete_status(
            user, status, raise_exception=True
        )

        status.delete()
