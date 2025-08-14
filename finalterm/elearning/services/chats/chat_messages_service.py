from elearning.models import ChatMessage, ChatParticipant, User
from elearning.exceptions import ServiceError


class ChatMessagesService:
    def __init__(self, chat_room_id: int):
        self.chat_room_id = chat_room_id

    def create_message(self, message: str, user: User):
        chat_participant = ChatParticipant.objects.get(
            chat_room_id=self.chat_room_id, user=user
        )

        if not chat_participant:
            raise ServiceError.permission_denied(
                "You are not a participant of this chat room"
            )

        return ChatMessage.objects.create(
            chat_room_id=self.chat_room_id,
            content=message,
            sender=user,
        )

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
