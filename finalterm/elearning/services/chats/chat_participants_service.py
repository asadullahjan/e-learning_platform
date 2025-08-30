from elearning.models import ChatParticipant, ChatRoom, User
from elearning.exceptions import ServiceError
from elearning.permissions.chats import ChatParticipantPolicy


class ChatParticipantsService:
    """
    Service for managing chat participants.

    Note: This service does NOT check student restrictions directly. For course
    chats, access is determined by enrollment status (enrollment.is_active),
    which is automatically managed by the restriction service.
    """

    @staticmethod
    def add_participant_to_chat(
        chat_room: ChatRoom, user: User, requesting_user: User
    ):
        """Add a user to a chat room"""
        # Check permissions using policy
        ChatParticipantPolicy.check_can_add_participant(
            requesting_user, chat_room, raise_exception=True
        )

        # For course chats, check if user is enrolled and enrollment is active
        if chat_room.chat_type == "course" and chat_room.course:
            # Check if user has active enrollment (this handles restrictions
            # automatically)
            enrollment_exists = chat_room.course.enrollments.filter(
                user=user, is_active=True
            ).exists()

            if not enrollment_exists:
                raise ServiceError.permission_denied(
                    f"User '{user.username}' must be enrolled in this course "
                    f"to participate in course chat"
                )

        # Check if user is already a participant
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user
        ).exists():
            raise ServiceError.conflict(
                f"User '{user.username}' is already a participant in this chat"
            )

        # Create new participant
        participant = ChatParticipant.objects.create(
            chat_room=chat_room, user=user, role="participant"
        )

        return participant

    @staticmethod
    def add_participants_to_chat(
        chat_room: ChatRoom, users: list[User], requesting_user: User
    ):
        """Add multiple users to a chat room"""
        # Check permissions using policy
        ChatParticipantPolicy.check_can_add_participant(
            requesting_user, chat_room, raise_exception=True
        )

        participants = []
        for user in users:
            # For course chats, check if user is enrolled and enrollment is
            # active
            if chat_room.chat_type == "course" and chat_room.course:
                # Check if user has active enrollment (this handles
                # restrictions automatically)
                enrollment_exists = chat_room.course.enrollments.filter(
                    user=user, is_active=True
                ).exists()

                if not enrollment_exists:
                    # Skip users without active enrollment instead of raising
                    # error for bulk operations
                    continue

            if not ChatParticipant.objects.filter(
                chat_room=chat_room, user=user
            ).exists():
                participant = ChatParticipant.objects.create(
                    chat_room=chat_room, user=user, role="participant"
                )
                participants.append(participant)

        return participants

    @staticmethod
    def remove_participant_from_chat(
        chat_room: ChatRoom, user: User, requesting_user: User
    ):
        """Remove a user from a chat room"""

        # Check permissions using policy
        ChatParticipantPolicy.check_can_remove_participant(
            requesting_user, chat_room, user, raise_exception=True
        )

        # Remove participant
        participant = ChatParticipant.objects.filter(
            chat_room=chat_room, user=user
        ).first()

        if participant:
            participant.delete()
            return True

        return False

    @staticmethod
    def join_chat(chat_room: ChatRoom, user: User):
        """Join a chat room"""
        # Check permissions using policy
        ChatParticipantPolicy.check_can_join_chat(
            user, chat_room, raise_exception=True
        )

        # For course chats, check if user is enrolled and enrollment is active
        if chat_room.chat_type == "course" and chat_room.course:
            # Check if user has active enrollment (this handles restrictions
            # automatically)
            enrollment_exists = chat_room.course.enrollments.filter(
                user=user, is_active=True
            ).exists()

            if not enrollment_exists:
                raise ServiceError.permission_denied(
                    "You must be enrolled in this course to join course chat"
                )

        # Check if already a participant
        participant, created = ChatParticipant.objects.get_or_create(
            chat_room=chat_room,
            user=user,
            defaults={"role": "participant", "is_active": True},
        )

        if not created and not participant.is_active:
            # Reactivate existing participant
            participant.is_active = True
            participant.save()

        return participant

    @staticmethod
    def leave_chat(chat_room: ChatRoom, user: User):
        """Leave a chat room"""
        # Remove participant
        participant = ChatParticipant.objects.filter(
            chat_room=chat_room, user=user
        ).first()

        if participant:
            participant.delete()
            return True

        return False

    @staticmethod
    def update_participant_role(
        chat_room: ChatRoom,
        requesting_user: User,
        user: User,
        new_role: str,
    ):
        """Update participant role"""
        # user is now a User instance, no need to query

        # Check permissions using policy
        ChatParticipantPolicy.check_can_update_participant_role(
            requesting_user, chat_room, user, raise_exception=True
        )

        try:
            participant = ChatParticipant.objects.get(
                chat_room=chat_room, user=user
            )
            participant.role = new_role
            participant.save()
            return participant
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                f"User '{user.username}' is not a participant " f"in this chat"
            )

    @staticmethod
    def deactivate_participant(
        chat_room: ChatRoom, user: User, requesting_user: User
    ):
        """Deactivate a participant"""

        # Check permissions using policy
        ChatParticipantPolicy.check_can_deactivate_participant(
            requesting_user, chat_room, user, raise_exception=True
        )

        # Deactivate participant
        participant = ChatParticipant.objects.filter(
            chat_room=chat_room, user=user
        ).first()

        if participant:
            participant.is_active = False
            participant.save()
            return participant

        return None

    @staticmethod
    def reactivate_participant(
        chat_room: ChatRoom, user: User, requesting_user: User
    ):
        """Reactivate a participant"""

        # Check permissions using policy
        ChatParticipantPolicy.check_can_reactivate_participant(
            requesting_user, chat_room, user, raise_exception=True
        )

        # For course chats, check if user is enrolled and enrollment is active
        if chat_room.chat_type == "course" and chat_room.course:
            # Check if user has active enrollment (this handles restrictions
            # automatically)
            enrollment_exists = chat_room.course.enrollments.filter(
                user=user, is_active=True
            ).exists()

            if not enrollment_exists:
                raise ServiceError.permission_denied(
                    "User must be enrolled in this course to participate in "
                    "course chat"
                )

        # Reactivate participant
        participant = ChatParticipant.objects.filter(
            chat_room=chat_room, user=user
        ).first()

        if participant:
            participant.is_active = True
            participant.save()
            return participant

        return None

    @staticmethod
    def get_participants(chat_room: ChatRoom, user: User):
        """Get participants of a chat room"""
        # Check permissions using policy
        ChatParticipantPolicy.check_can_get_participants(
            user, chat_room, raise_exception=True
        )

        return ChatParticipant.objects.filter(
            chat_room=chat_room,
            is_active=True,
        ).select_related("user")

    @staticmethod
    def get_active_participants(chat_room: ChatRoom, user: User):
        """Get active participants of a chat room"""
        # Check permissions using policy
        ChatParticipantPolicy.check_can_get_participants(
            user, chat_room, raise_exception=True
        )

        return ChatParticipant.objects.filter(
            chat_room=chat_room, is_active=True
        ).select_related("user")
