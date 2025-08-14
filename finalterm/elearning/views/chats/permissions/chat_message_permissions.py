from rest_framework.permissions import BasePermission


class ChatMessagePermission(BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list"]:
            return True
        if (
            view.action in ["create", "partial_update", "destroy"]
            and request.user.is_authenticated
        ):
            return True
        return False
