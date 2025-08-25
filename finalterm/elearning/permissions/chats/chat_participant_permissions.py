from rest_framework.permissions import BasePermission
from elearning.models import ChatRoom
from elearning.services.chats.chat_utils import ChatUtils


class ChatParticipantPermission(BasePermission):
    def has_permission(self, request, view):
        chat_room_pk = view.kwargs.get("chat_room_pk")

        if not chat_room_pk:
            return False

        try:
            chat_room = ChatRoom.objects.get(id=chat_room_pk)
            request.chat_room = chat_room
        except ChatRoom.DoesNotExist:
            return False

        if view.action == "list":
            return True

        if not request.user.is_authenticated:
            return False

        if view.action == "create":
            # Check if user is adding someone else
            # (admin only) or joining themselves
            username = request.data.get("username")
            if username:
                # Adding another user - only admins can do this
                return ChatUtils.is_user_admin(chat_room, request.user)
            else:
                # Joining themselves - check if chat is public
                return chat_room.is_public

        if view.action == "update_role":
            # Only admins can update roles
            return ChatUtils.is_user_admin(chat_room, request.user)

        if view.action in ["deactivate", "reactivate"]:
            # Users can deactivate/reactivate themselves,
            # admins can do it for others
            return True

        if view.action == "destroy":
            # Only admins can remove participants
            return ChatUtils.is_user_admin(chat_room, request.user)

        # Default: only chat creator has access
        return request.user == chat_room.created_by
