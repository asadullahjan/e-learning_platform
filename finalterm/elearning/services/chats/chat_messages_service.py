from elearning.models import ChatMessage, User
from elearning.exceptions import ServiceError


class ChatMessagesService:
    def __init__(self, chat_room_id: int):
        self.chat_room_id = chat_room_id

    def create_message(self, user, content):
        """Create a new message in the chat room"""
        
        message = ChatMessage.objects.create(
            chat_room_id=self.chat_room_id,
            sender=user,
            content=content,
        )
        
        return message

    def update_message(self, message: str, user: User, message_id: int):
        chat_message = ChatMessage.objects.get(id=message_id)
        if chat_message.sender != user:
            raise ServiceError.permission_denied(
                "You are not the sender of this message"
            )
        chat_message.content = message
        chat_message.save()
        return chat_message

    def delete_message(self, message_id: int, user: User):
        chat_message = ChatMessage.objects.get(id=message_id)
        if chat_message.sender != user:
            raise ServiceError.permission_denied(
                "You are not the sender of this message"
            )
        chat_message.delete()
