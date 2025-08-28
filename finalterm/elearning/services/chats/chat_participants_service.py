from elearning.models import ChatParticipant, ChatRoom, User
from elearning.exceptions import ServiceError
from elearning.permissions.chats.chat_participant_permissions import (
    ChatParticipantPolicy,
)


class ChatParticipantsService:
    """Service for managing chat participants"""

    @staticmethod
    def add_user_to_chat_by_username(
        chat_room: ChatRoom, username: str, requesting_user: User
    ):
        """Add a user to a chat room by username"""
        # Check permissions using policy
        ChatParticipantPolicy.check_can_add_participant(
            requesting_user, chat_room, raise_exception=True
        )

        try:
            user = User.objects.select_related().get(
                username=username, is_active=True
            )
        except User.DoesNotExist:
            raise ServiceError.not_found(f"User '{username}' not found")

        # Check if user is restricted from course chat
        if chat_room.chat_type == "course" and chat_room.course:
            from elearning.services.courses.student_restriction_service import (
                StudentRestrictionService,
            )

            restriction_info = StudentRestrictionService.get_restriction_info(
                user, chat_room.course
            )

            if restriction_info["is_restricted"]:
                if restriction_info["restriction_type"] == "teacher_all_courses":
                    error_msg = (
                        f"User '{username}' is restricted from accessing "
                        f"all courses by {restriction_info['teacher']}. "
                        f"Reason: {restriction_info['reason']}"
                    )
                else:  # course-specific
                    error_msg = (
                        f"User '{username}' is restricted from accessing "
                        f"this course. Reason: {restriction_info['reason']}"
                    )
                raise ServiceError.permission_denied(error_msg)

        # Check if user is already a participant
        if ChatParticipant.objects.filter(
            chat_room=chat_room, user=user
        ).exists():
            raise ServiceError.conflict(
                f"User '{username}' is already a participant in this chat"
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
            # Check if user is restricted from course chat
            if chat_room.chat_type == "course" and chat_room.course:
                from elearning.services.courses.student_restriction_service import (
                    StudentRestrictionService,
                )
                
                restriction_info = StudentRestrictionService.get_restriction_info(
                    user, chat_room.course
                )
                
                if restriction_info["is_restricted"]:
                    # Skip restricted users instead of raising error for bulk operations
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
        """Remove a participant from a chat room (soft delete)"""
        # Check permissions using policy
        ChatParticipantPolicy.check_can_remove_participant(
            requesting_user, chat_room, user, raise_exception=True
        )

        try:
            participant = ChatParticipant.objects.select_related(
                'user', 'chat_room', 'chat_room__course'
            ).get(
                chat_room=chat_room, user=user, is_active=True
            )
            participant.is_active = False
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                f"User '{user.username}' is not an active participant " f"in this chat"
            )

    @staticmethod
    def join_public_chat(chat_room_id: int, user: User):
        """Join a public chat room"""
        # Get chat room and check if it exists
        try:
            chat_room = ChatRoom.objects.select_related('course').get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            raise ServiceError.not_found("Chat room not found")

        # Check if user can join this chat
        ChatParticipantPolicy.check_can_join_chat(
            user, chat_room, raise_exception=True
        )

        # Check if user is restricted from course chat
        if chat_room.chat_type == "course" and chat_room.course:
            from elearning.services.courses.student_restriction_service import (
                StudentRestrictionService,
            )
            
            restriction_info = StudentRestrictionService.get_restriction_info(
                user, chat_room.course
            )
            
            if restriction_info["is_restricted"]:
                if restriction_info["restriction_type"] == "teacher_all_courses":
                    error_msg = (
                        f"You are restricted from accessing all courses by "
                        f"{restriction_info['teacher']}. "
                        f"Reason: {restriction_info['reason']}"
                    )
                else:  # course-specific
                    error_msg = (
                        f"You are restricted from accessing this course. "
                        f"Reason: {restriction_info['reason']}"
                    )
                raise ServiceError.permission_denied(error_msg)

        # Check if already a participant
        participant, created = ChatParticipant.objects.get_or_create(
            chat_room=chat_room, user=user, defaults={"role": "participant", "is_active": True}
        )

        if not created and not participant.is_active:
            # Reactivate existing participant
            participant.is_active = True
            participant.save()

        return participant

    @staticmethod
    def leave_chat(chat_room_id: int, user: User):
        """Leave a chat room (deactivate participation)"""
        # Get chat room and check if it exists
        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            raise ServiceError.not_found("Chat room not found")

        try:
            participant = ChatParticipant.objects.select_related(
                'user', 'chat_room', 'chat_room__course'
            ).get(
                chat_room=chat_room, user=user
            )
            participant.is_active = False
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            return False

    @staticmethod
    def update_participant_role(
        chat_room: ChatRoom, admin_user: User, target_user: User, new_role: str
    ):
        """Update a participant's role (admin only)"""
        # Check if admin user can update roles
        ChatParticipantPolicy.check_can_update_participant_role(
            admin_user, chat_room, target_user, raise_exception=True
        )

        try:
            participant = ChatParticipant.objects.select_related(
                'user', 'chat_room', 'chat_room__course'
            ).get(
                chat_room=chat_room, user=target_user
            )
            participant.role = new_role
            participant.save()
            return participant
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                f"User '{target_user.username}' is not a participant "
                f"in this chat"
            )

    @staticmethod
    def deactivate_chat_for_user(
        chat_room: ChatRoom, user: User, requesting_user: User = None
    ):
        """Deactivate a user's participation in a chat"""
        # If requesting_user is provided, check permissions
        if requesting_user and requesting_user != user:
            ChatParticipantPolicy.check_can_deactivate_participant(
                requesting_user, chat_room, user, raise_exception=True
            )

        try:
            participant = ChatParticipant.objects.select_related(
                'user', 'chat_room', 'chat_room__course'
            ).get(
                chat_room=chat_room, user=user
            )
            participant.is_active = False
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                f"User '{user.username}' is not a participant " f"in this chat"
            )

    @staticmethod
    def deactivate_participant_by_admin(
        chat_room: ChatRoom, admin_user: User, target_user: User
    ):
        """Deactivate a participant from a chat (admin only)"""
        # Check if admin user can deactivate participants
        ChatParticipantPolicy.check_can_deactivate_participant(
            admin_user, chat_room, target_user, raise_exception=True
        )

        try:
            participant = ChatParticipant.objects.select_related(
                'user', 'chat_room', 'chat_room__course'
            ).get(
                chat_room=chat_room, user=target_user
            )
            participant.is_active = False
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            raise ServiceError.not_found(
                f"User '{target_user.username}' is not a participant "
                f"in this chat"
            )

    @staticmethod
    def reactivate_chat_for_user(
        chat_room: ChatRoom, user: User, requesting_user: User = None
    ):
        """Reactivate a user's participation in a chat"""
        # If requesting_user is provided, check permissions
        if requesting_user and requesting_user != user:
            ChatParticipantPolicy.check_can_reactivate_participant(
                requesting_user, chat_room, user, raise_exception=True
            )

        # Check if user is restricted from course chat
        if chat_room.chat_type == "course" and chat_room.course:
            from elearning.services.courses.student_restriction_service import (
                StudentRestrictionService,
            )
            
            restriction_info = StudentRestrictionService.get_restriction_info(
                user, chat_room.course
            )
            
            if restriction_info["is_restricted"]:
                if restriction_info["restriction_type"] == "teacher_all_courses":
                    error_msg = (
                        f"You are restricted from accessing all courses by "
                        f"{restriction_info['teacher']}. "
                        f"Reason: {restriction_info['reason']}"
                    )
                else:  # course-specific
                    error_msg = (
                        f"You are restricted from accessing this course. "
                        f"Reason: {restriction_info['reason']}"
                    )
                raise ServiceError.permission_denied(error_msg)

        try:
            participant = ChatParticipant.objects.select_related(
                'user', 'chat_room', 'chat_room__course'
            ).get(
                chat_room=chat_room, user=user
            )
            participant.is_active = True
            participant.save()
            return True
        except ChatParticipant.DoesNotExist:
            # Create new participant if doesn't exist
            participant = ChatParticipant.objects.create(
                chat_room=chat_room, user=user, role="participant", is_active=True
            )
            return True

    @staticmethod
    def get_chat_participants(
        chat_room_id: int,
        requesting_user: User,
        is_active: bool = True,
    ):
        """Get all participants for a chat room"""
        # Get chat room and check if it exists
        try:
            chat_room = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            raise ServiceError.not_found("Chat room not found")

        # Check if user can get participants of this chat room
        ChatParticipantPolicy.check_can_get_participants(
            requesting_user, chat_room, raise_exception=True
        )

        return ChatParticipant.objects.filter(
            chat_room=chat_room, is_active=is_active
        ).select_related("user")
