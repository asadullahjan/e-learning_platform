"""
Chat-related permissions for the eLearning platform.

This package contains permission classes that control access to chat
functionality such as chat rooms, messages, and participants.
"""

from .chat_room_permissions import ChatRoomPermission
from .chat_message_permissions import ChatMessagePermission
from .chat_participant_permissions import ChatParticipantPermission

__all__ = [
    "ChatRoomPermission",
    "ChatMessagePermission",
    "ChatParticipantPermission",
]
