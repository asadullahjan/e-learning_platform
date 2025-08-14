from rest_framework.permissions import BasePermission


class ChatRoomPermission(BasePermission):
    """Handles permissions for ChatRoom operations"""

    def has_permission(self, request, view):
        # Handle list/retrieve actions first
        if view.action in ["list", "retrieve"]:
            return True  # Anyone can list/retrieve

        # Check authentication for other actions
        if not request.user.is_authenticated:
            return False

        # Handle create action with proper return
        if view.action == "create":
            chat_type = request.data.get("chat_type")
            course = request.data.get("course")

            if chat_type == "course":
                # Only teachers can create course chatrooms
                if request.user.role != "teacher":
                    return False
                # Course must exist and user must be the teacher
                if (
                    course
                    and not request.user.courses_taught.filter(
                        id=course
                    ).exists()
                ):
                    return False

            return True  # Allow creation for other chat types

        # Default to allowing other actions
        # (object permissions will handle them)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Handle retrieve action (individual chat access)
        if view.action == "retrieve":
            # Public chats: accessible to everyone
            if obj.is_public:
                return True

            # Private chats: only accessible to participants
            if obj.participants.filter(user=user, is_active=True).exists():
                return True

            # Course chats: accessible to course teacher
            if obj.course and obj.course.teacher == user:
                return True

            return False

        # # Handle update/destroy actions
        # if view.action in ["update", "partial_update", "destroy"]:
        #     # Only creator can modify
        #     return obj.created_by == user

        # # Handle custom actions
        # if view.action in ["add_participants", "change_participant_role"]:
        #     # Only admins can manage participants
        #     try:
        #         participant = obj.participants.get(user=user)
        #         return participant.role == "admin"
        #     except ChatParticipant.DoesNotExist:
        #         return False

        return obj.created_by == user  # For now only creator can modify
