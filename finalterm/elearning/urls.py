from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views

app_name = "elearning"

# Main router
router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"courses", views.CourseViewSet, basename="course")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(r"chats", views.ChatRoomViewSet, basename="chat")
router.register(r"statuses", views.StatusViewSet, basename="status")
router.register(
    r"restrictions", views.StudentRestrictionViewSet, basename="restriction"
)
router.register(
    r"notifications", views.NotificationViewSet, basename="notification"
)
router.register(r"auth", views.AuthViewSet, basename="auth")

# Courses router
courses_router = NestedDefaultRouter(router, r"courses", lookup="course")
courses_router.register(
    r"lessons", views.CourseLessonViewSet, basename="course-lessons"
)
courses_router.register(
    r"feedbacks", views.FeedbackViewSet, basename="course-feedbacks"
)
courses_router.register(
    r"enrollments",
    views.CourseEnrollmentViewSet,
    basename="course-enrollments",
)

# Chats router
chats_router = NestedDefaultRouter(router, r"chats", lookup="chat_room")
chats_router.register(
    r"participants", views.ChatParticipantViewSet, basename="chat-participant"
)
chats_router.register(
    r"messages", views.ChatMessageViewSet, basename="chat-message"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(courses_router.urls)),
    path("", include(chats_router.urls)),
]
