from elearning.models import User
from elearning.exceptions import ServiceError
from elearning.permissions.users.user_permissions import UserPolicy


class UserService:
    """
    Service for managing user operations and business logic.
    """

    @staticmethod
    def get_user_by_username(username):
        """
        Get user by username.

        Args:
            username: Username string

        Returns:
            User instance

        Raises:
            ServiceError: If user not found
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise ServiceError.not_found(f"User '{username}' not found")

    @staticmethod
    def can_user_access_profile(requesting_user, target_user):
        """
        Check if a user can access another user's profile.

        This method implements the business rules for profile access:
        - Users can always view their own profile
        - Teachers can view student profiles
        - Students can view teacher profiles
        - Anonymous users cannot view any profiles

        Args:
            requesting_user: User attempting to access the profile
            target_user: User whose profile is being accessed

        Returns:
            bool: True if access is allowed, False otherwise
        """
        return UserPolicy.check_can_view_profile(requesting_user, target_user)

    @staticmethod
    def get_user_with_permission_check(user_id: int, requesting_user: User):
        """Get user with permission check"""
        try:
            user = User.objects.get(id=user_id)
            # Check if requesting user can view this profile
            UserPolicy.check_can_view_profile(
                requesting_user, user, raise_exception=True
            )
            return user
        except User.DoesNotExist:
            raise ServiceError.not_found("User not found")

    @staticmethod
    def update_user_profile(user: User, requesting_user: User, **kwargs):
        """Update user profile with permission check"""
        # Check if requesting user can modify this profile
        UserPolicy.check_can_modify_profile(
            requesting_user, user, raise_exception=True
        )

        # Update user fields
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)

        user.save()
        return user

    @staticmethod
    def delete_user(target_user: User, requesting_user: User):
        """Delete user with permission check"""
        # Check if requesting user can delete this user
        UserPolicy.check_can_modify_profile(
            requesting_user, target_user, raise_exception=True
        )

        # Delete the user
        target_user.delete()

    @staticmethod
    def populate_user_computed_fields(user: User):
        """Populate computed fields for user serialization"""
        # Get course counts
        user._courses_taught_count = user.courses_taught.count()
        user._courses_enrolled_count = user.enrollments.filter(
            is_active=True
        ).count()

        return user

    @staticmethod
    def get_users_with_computed_fields():
        """Get users with computed fields populated"""
        users = User.objects.all()

        # Populate computed fields for each user
        for user in users:
            UserService.populate_user_computed_fields(user)

        return users
