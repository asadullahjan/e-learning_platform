from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views

app_name = "elearning"

# Main router
router = DefaultRouter()
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(r"chats", views.ChatRoomViewSet, basename="chat")
router.register(r"statuses", views.StatusViewSet, basename="status")

# Nested routers
courses_router = NestedDefaultRouter(router, r"courses", lookup="course")
courses_router.register(
    r"lessons", views.CourseLessonViewSet, basename="course-lessons"
)

chats_router = NestedDefaultRouter(router, r"chats", lookup="chat_room")
chats_router.register(
    r"participants", views.ChatParticipantViewSet, basename="chat-participant"
)
chats_router.register(
    r"messages", views.ChatMessageViewSet, basename="chat-message"
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
    path("", include(courses_router.urls)),
    path("", include(chats_router.urls)),
]
