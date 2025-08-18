from rest_framework.permissions import BasePermission
from elearning.models import ChatParticipant


class ChatMessagePermission(BasePermission):
    def has_permission(self, request, view):
        # Must be authenticated for all except list
        if view.action == "list":
            return request.user.is_authenticated

        if view.action == "create":
            chat_room_id = request.data.get("chat_room") or view.kwargs.get(
                "chat_room_id"
            )
            return (
                request.user.is_authenticated
                and chat_room_id
                and self._is_participant(request.user, chat_room_id)
            )

        if view.action in ["partial_update", "destroy"]:
            return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ["partial_update", "destroy"]:
            # Sender can always edit/delete their own messages
            if obj.sender == request.user:
                return True
            # Otherwise must be admin in chat room
            return self._is_admin(request.user, obj.chat_room.id)
        return True

    def _is_participant(self, user, chat_room_id):
        """Check if user is an active participant of the chat room"""
        try:
            ChatParticipant.objects.get(
                chat_room_id=chat_room_id, user=user, is_active=True
            )
            return True
        except ChatParticipant.DoesNotExist:
            return False

    def _is_admin(self, user, chat_room_id):
        """Check if user is an admin of the chat room"""
        try:
            ChatParticipant.objects.get(
                chat_room_id=chat_room_id, user=user, role="admin"
            )
            return True
        except ChatParticipant.DoesNotExist:
            return False
