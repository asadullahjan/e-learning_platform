from elearning.models import ChatMessage, User, ChatRoom
from elearning.exceptions import ServiceError
from elearning.permissions.chats.chat_message_permissions import (
    ChatMessagePolicy
)


class ChatMessagesService:
    def __init__(self, chat_room_id: int):
        self.chat_room_id = chat_room_id

    def create_message(self, user, content):
        """Create a new message in the chat room"""
        # Check if user can create message in this chat room
        try:
            chat_room = ChatRoom.objects.get(id=self.chat_room_id)
            ChatMessagePolicy.check_can_create_message(
                user, chat_room, raise_exception=True
            )
        except ChatRoom.DoesNotExist:
            raise ServiceError.not_found("Chat room not found")
        
        message = ChatMessage.objects.create(
            chat_room_id=self.chat_room_id,
            sender=user,
            content=content,
        )
        
        return message

    def update_message(self, message: str, user: User, message_id: int):
        """Update message with permission check"""
        try:
            chat_message = ChatMessage.objects.get(id=message_id)
        except ChatMessage.DoesNotExist:
            raise ServiceError.not_found("Message not found")
        
        # Check if user can modify this message
        ChatMessagePolicy.check_can_modify_message(
            user, chat_message, raise_exception=True
        )
        
        chat_message.content = message
        chat_message.save()
        return chat_message

    def delete_message(self, message_id: int, user: User):
        """Delete message with permission check"""
        try:
            chat_message = ChatMessage.objects.get(id=message_id)
        except ChatMessage.DoesNotExist:
            raise ServiceError.not_found("Message not found")
        
        # Check if user can delete this message
        ChatMessagePolicy.check_can_modify_message(
            user, chat_message, raise_exception=True
        )
        
        chat_message.delete()

    def get_message_with_permission_check(self, message_id: int, user: User):
        """Get message with permission check"""
        try:
            message = ChatMessage.objects.get(id=message_id)
            # Check if user can view this message
            ChatMessagePolicy.check_can_view_message(
                user, message, raise_exception=True
            )
            return message
        except ChatMessage.DoesNotExist:
            raise ServiceError.not_found("Message not found")

    def get_chat_messages(self, user: User, limit: int = 50):
        """Get chat messages with permission check"""
        # Check if user can access this chat room
        try:
            chat_room = ChatRoom.objects.get(id=self.chat_room_id)
            from elearning.permissions.chats.chat_room_permissions import (
                ChatPolicy
            )
            ChatPolicy.check_can_access_chat_room(
                user, chat_room, raise_exception=True
            )
        except ChatRoom.DoesNotExist:
            raise ServiceError.not_found("Chat room not found")
        
        return ChatMessage.objects.filter(
            chat_room_id=self.chat_room_id
        ).order_by("-created_at")[:limit]
