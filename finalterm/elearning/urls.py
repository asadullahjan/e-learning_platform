from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "elearning"

# Create router for ViewSets
router = DefaultRouter()
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(
    r"chats",
    views.ChatRoomViewSet,
    basename="chat",
)
router.register(
    r"chats/(?P<chat_room_id>\d+)/participants",
    views.ChatParticipantViewSet,
    basename="chat-participant",
)
router.register(
    r"chats/(?P<chat_room_id>\d+)/messages",
    views.ChatMessageViewSet,
    basename="chat-message",
)

urlpatterns = [
    # Authentication endpoints
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("auth/profile/", views.user_profile, name="profile"),
    path("auth/profile/update/", views.update_profile, name="update_profile"),
    # Include router URLs
    path("", include(router.urls)),
]
