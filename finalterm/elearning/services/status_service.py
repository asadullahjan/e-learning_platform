from elearning.models import Status, User
from elearning.exceptions import ServiceError


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
