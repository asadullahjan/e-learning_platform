from django.db import transaction, models
from elearning.models import ChatParticipant, ChatRoom, User
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
    def find_or_create_direct_chat(creator: User, other_username: str):
        """Find existing direct chat or create new one with another user"""
        try:
            other_user = User.objects.get(
                username=other_username, is_active=True
            )
        except User.DoesNotExist:
            raise ValueError(f"User '{other_username}' not found")

        if creator == other_user:
            raise ValueError("Cannot create chat with yourself")

        # Check if direct chat already exists
        existing_chat = ChatService._find_existing_direct_chat(
            creator, other_user
        )

        if existing_chat:
            # Reactivate if needed
            ChatParticipantsService.reactivate_chat_for_user(
                existing_chat, creator
            )
            existing_chat.save()
            return existing_chat, False

        # Create new direct chat
        chat_name = f"Direct chat: {creator.username} & {other_user.username}"
        chat_room = ChatRoom.objects.create(
            name=chat_name,
            chat_type="direct",
            created_by=creator,
            is_public=False,
        )

        # Add both users as participants
        ChatParticipant.objects.create(
            chat_room=chat_room, user=creator, role="participant"
        )

        ChatParticipant.objects.create(
            chat_room=chat_room, user=other_user, role="participant"
        )

        return chat_room, True

    @staticmethod
    def get_active_chats_for_user(user):
        """Get all active chats for a specific user"""
        return ChatRoom.objects.filter(
            participants__user=user, participants__is_active=True
        )

    @staticmethod
    def get_user_chats(user):
        """Get only the chats where the user is an active participant"""
        if not user.is_authenticated:
            return ChatRoom.objects.none()

        return ChatRoom.objects.filter(
            participants__user=user, participants__is_active=True
        ).distinct()

    @staticmethod
    def get_all_available_chats(user):
        """Get all chats available to the user
        (public, participated, or teachable)"""
        if not user.is_authenticated:
            # Anonymous users only see public chats
            return ChatRoom.objects.filter(is_public=True)

        # Authenticated users see:
        # 1. Public chats
        # 2. Private chats they participate in
        # 3. Course chats they teach
        return ChatRoom.objects.filter(
            models.Q(is_public=True)
            | models.Q(participants__user=user, participants__is_active=True)
            | models.Q(course__teacher=user)
        ).distinct()
