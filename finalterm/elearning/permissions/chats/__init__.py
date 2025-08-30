"""
Chat-related permissions for the eLearning platform.

This package contains permission classes that control access to chat
functionality such as chat rooms, messages, and participants.
"""

# Permissions
from .chat_room_permissions import ChatRoomPermission
from .chat_message_permissions import ChatMessagePermission
from .chat_participant_permissions import ChatParticipantPermission

# Policies
from .chat_room_permissions import ChatPolicy
from .chat_message_permissions import ChatMessagePolicy
from .chat_participant_permissions import ChatParticipantPolicy

__all__ = [
    # Permissions
    "ChatRoomPermission",
    "ChatMessagePermission",
    "ChatParticipantPermission",
    # Policies
    "ChatPolicy",
    "ChatMessagePolicy",
    "ChatParticipantPolicy",
]
