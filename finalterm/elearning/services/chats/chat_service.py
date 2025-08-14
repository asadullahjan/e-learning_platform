from django.db import transaction
from django.contrib.auth.models import User
from elearning.models import ChatParticipant, ChatRoom
from elearning.services.chats.chat_participants_service import (
    ChatParticipantsService,
)


class ChatService:
    @staticmethod
    @transaction.atomic
    def create_chat_room(validated_data, creator: User) -> ChatRoom:
        """
        Create a chat room and add participants based on chat type
        """
        participants = validated_data.pop("participants", [])
        chat_type = validated_data.get("chat_type")

        # if chat_type is direct, we need to check if the chat already exists
        if chat_type == "direct":
            existing_chat = ChatService._find_existing_direct_chat(
                creator, participants[0]
            )
            # if the chat already exists, return it and update the is_active
            if existing_chat:
                ChatParticipantsService.reactivate_chat_for_user(
                    existing_chat, creator
                )
                existing_chat.save()
                return existing_chat

        # create the chat room
        chat_room = ChatRoom.objects.create(
            created_by=creator, **validated_data
        )

        # add creator as admin
        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=creator,
            role="participant" if chat_type == "direct" else "admin",
        )

        # add participants to the chat room
        ChatParticipantsService.add_participants_to_chat(
            chat_room, participants
        )

        return chat_room

    @staticmethod
    def _find_existing_direct_chat(
        creator: User, other_user: User
    ) -> ChatRoom:
        """Find existing direct chat between two users"""
        creator_chats = ChatRoom.objects.filter(
            chat_type="direct", participants__user=creator
        )

        for chat in creator_chats:
            if ChatParticipant.objects.filter(
                chat_room=chat, user=other_user
            ).exists():
                return chat

        return None

    @staticmethod
    def get_active_chats_for_user(user):
        """Get all active chats for a specific user"""
        return ChatRoom.objects.filter(
            participants__user=user, participants__is_active=True
        )
