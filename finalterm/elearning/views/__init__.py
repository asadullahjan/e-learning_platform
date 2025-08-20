# Import all views for easy access
from .auth_views import register, login_view, logout_view
from .profile_views import user_profile, update_profile
from .courses import CourseViewSet, CourseLessonViewSet, EnrollmentViewSet
from .chats.chat_room_views import ChatRoomViewSet
from .chats.chat_participant_views import ChatParticipantViewSet
from .chats.chat_message_views import ChatMessageViewSet
from .status_views import StatusViewSet
from .user_views import get_user_by_username, search_users

__all__ = [
    "register",
    "login_view",
    "logout_view",
    "user_profile",
    "update_profile",
    "CourseViewSet",
    "CourseLessonViewSet",
    "EnrollmentViewSet",
    "ChatRoomViewSet",
    "ChatParticipantViewSet",
    "ChatMessageViewSet",
    "StatusViewSet",
    "get_user_by_username",
    "search_users",
]
