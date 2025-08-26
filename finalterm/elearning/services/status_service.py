from elearning.models import Status, User
from elearning.exceptions import ServiceError
from elearning.services.notification_service import NotificationService
from elearning.permissions.users.status_permissions import StatusPolicy


class StatusService:
    """Service class for status-related business logic"""

    @staticmethod
    def get_user_statuses(user: User) -> list[Status]:
        """Get status updates for a specific user"""
        return Status.objects.filter(user=user).order_by("-created_at")

    @staticmethod
    def get_my_statuses(user: User) -> list[Status]:
        """Get current user's status updates"""
        return Status.objects.filter(user=user).order_by("-created_at")

    @staticmethod
    def validate_user_exists(user_id: int) -> User:
        """Validate that a user exists and return the user object"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ServiceError("User not found")

    @staticmethod
    def create_status(user: User, content: str) -> Status:
        """Create a new status and notify followers"""
        # Check if user can create status
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
    def get_status_with_permission_check(status_id: int, user: User):
        """Get status with permission check"""
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
    def update_status(status: Status, user: User, content: str):
        """Update status with permission check"""
        # Check if user can modify this status
        StatusPolicy.check_can_modify_status(
            user, status, raise_exception=True
        )
        
        status.content = content
        status.save()
        return status

    @staticmethod
    def delete_status(status: Status, user: User):
        """Delete status with permission check"""
        # Check if user can delete this status
        StatusPolicy.check_can_delete_status(
            user, status, raise_exception=True
        )
        
        status.delete()
