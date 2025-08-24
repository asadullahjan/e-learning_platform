from elearning.models import Status, User
from elearning.exceptions import ServiceError
from elearning.services.notification_service import NotificationService


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
