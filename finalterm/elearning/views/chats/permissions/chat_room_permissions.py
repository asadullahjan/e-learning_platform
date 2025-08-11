from rest_framework.permissions import BasePermission


class ChatRoomPermission(BasePermission):
    """Handles permissions for ChatRoom operations"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.action == "create":
            # Check if user is trying to create a course chatroom
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

            return True  # Allow other chat types for authenticated users

        if view.action == "list":
            return True

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if view.action in ["retrieve", "list"]:
            return (
                obj.participants.filter(user=user).exists()
                or obj.is_public
                or (
                    user.role == "teacher"
                    and obj.course
                    and obj.course.teacher == user
                )
            )

        if view.action in ["update", "partial_update", "destroy"]:
            return obj.created_by == user

        return False
