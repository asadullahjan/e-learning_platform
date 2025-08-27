from django.db import transaction, models
from elearning.models import ChatParticipant, ChatRoom, User
from elearning.services.chats.chat_participants_service import (
    ChatParticipantsService,
)
from elearning.exceptions import ServiceError
from elearning.permissions.chats.chat_room_permissions import ChatPolicy


class ChatService:
    """
    Service for managing chat operations and business logic.
    """

    @staticmethod
    @transaction.atomic
    def create_chat_room(validated_data, creator: User) -> ChatRoom:
        """
        Create a chat room with participants.

        This method creates a chat room and adds participants based on the
        validated data. The operation is wrapped in a database transaction
        to ensure data consistency.

        Args:
            validated_data: Validated chat room data from serializer
            creator: User creating the chat room

        Returns:
            ChatRoom instance with participants added
        """
        # Extract data
        chat_type = validated_data.get("chat_type")
        course = validated_data.get("course")
        participants = validated_data.get("participants", [])

        # Check if user can create this type of chat room
        ChatPolicy.check_can_create_chat_room(
            creator, chat_type, course, raise_exception=True
        )
        
        # For direct chats, check if one already exists
        if chat_type == "direct" and len(participants) == 1:
            other_user_id = participants[0]
            try:
                other_user = User.objects.get(id=other_user_id, is_active=True)
                existing_chat = ChatService._find_existing_direct_chat(
                    creator, other_user
                )
                if existing_chat:
                    # Reactivate if needed and return existing chat
                    ChatParticipantsService.reactivate_chat_for_user(
                        existing_chat, creator
                    )
                    existing_chat.save()
                    return existing_chat
            except User.DoesNotExist:
                raise ServiceError.not_found(
                    f"User with ID {other_user_id} not found"
                )

        # Create the chat room
        chat_room = ChatRoom.objects.create(
            name=validated_data["name"],
            chat_type=chat_type,
            course=course,
            is_public=validated_data.get("is_public", False),
            created_by=creator,
        )

        # Add creator as admin participant (except for direct chats)
        creator_role = "participant" if chat_type == "direct" else "admin"
        ChatParticipant.objects.create(
            chat_room=chat_room, user=creator, role=creator_role
        )

        # Add other participants if specified
        if participants:
            participants = User.objects.filter(id__in=participants)
            ChatParticipantsService.add_participants_to_chat(
                chat_room, list(participants), creator
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
            raise ServiceError.not_found(f"User '{other_username}' not found")

        if creator == other_user:
            raise ServiceError.bad_request("Cannot create chat with yourself")

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
    def get_chat_with_permission_check(chat_id: int, user: User):
        """Get chat with permission check"""
        try:
            chat_room = ChatRoom.objects.get(id=chat_id)
            # Check if user can access this chat room
            ChatPolicy.check_can_access_chat_room(
                user, chat_room, raise_exception=True
            )
            return chat_room
        except ChatRoom.DoesNotExist:
            raise ServiceError.not_found("Chat room not found")

    @staticmethod
    def update_chat_room(chat_room: ChatRoom, user: User, **kwargs):
        """Update chat room with permission check"""
        # Check if user can modify this chat room
        ChatPolicy.check_can_modify_chat_room(
            user, chat_room, raise_exception=True
        )

        # Update chat room fields
        for field, value in kwargs.items():
            if hasattr(chat_room, field):
                setattr(chat_room, field, value)

        chat_room.save()
        return chat_room

    @staticmethod
    def delete_chat_room(chat_room: ChatRoom, user: User):
        """Delete chat room with permission check"""
        # Check if user can modify this chat room
        ChatPolicy.check_can_modify_chat_room(
            user, chat_room, raise_exception=True
        )

        # Delete the chat room (this will cascade to related objects)
        chat_room.delete()

    @staticmethod
    def populate_chat_computed_fields(chat_room: ChatRoom, user: User = None):
        """Populate computed fields for chat room serialization"""
        if user and user.is_authenticated:
            try:
                participant = ChatParticipant.objects.get(
                    chat_room=chat_room, user=user, is_active=True
                )
                chat_room._current_user_status = {
                    "is_participant": True,
                    "role": participant.role,
                }
            except ChatParticipant.DoesNotExist:
                # Debug: Check if participant exists but is inactive
                inactive_participant = ChatParticipant.objects.filter(
                    chat_room=chat_room, user=user
                ).first()

                if inactive_participant:
                    # Participant exists but is inactive
                    chat_room._current_user_status = {
                        "is_participant": False,
                        "role": inactive_participant.role,
                    }
                else:
                    # No participant record found
                    chat_room._current_user_status = {
                        "is_participant": False,
                        "role": None,
                    }
        else:
            chat_room._current_user_status = {
                "is_participant": False,
                "role": None,
            }

        return chat_room

    @staticmethod
    def get_chat_rooms(user: User = None):
        """Get chat rooms with permission checking"""
        if not user or not user.is_authenticated:
            # Unauthenticated users only see public chats
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

    @staticmethod
    def get_chats_with_computed_fields(user: User = None):
        """Get chat rooms with computed fields populated"""
        chat_rooms = ChatService.get_chat_rooms(user)

        # Populate computed fields for each chat room
        for chat_room in chat_rooms:
            ChatService.populate_chat_computed_fields(chat_room, user)

        return chat_rooms
