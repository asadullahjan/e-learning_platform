from rest_framework.permissions import BasePermission

from elearning.models import ChatRoom


class ChatParticipantPermissions(BasePermission):
    def has_permission(self, request, view):
        chat_room_id = view.kwargs.get("chat_room_id")

        if not chat_room_id:
            return False

        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
            request.chat_room = chat_room
        except ChatRoom.DoesNotExist:
            return False

        if view.action == "list_chat_participants":
            return True

        if not request.user.is_authenticated:
            return False

        if view.action == "create_chat_participant":
            return True

        return request.user == chat_room.created_by
