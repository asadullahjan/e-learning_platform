from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import chats, courses
from . import views

app_name = "elearning"

# =============================================================================
# MAIN ROUTER - Top-level API endpoints
# =============================================================================
router = DefaultRouter()

# User management endpoints
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"auth", views.AuthViewSet, basename="auth")

# Course management endpoints
router.register(r"courses", courses.CourseViewSet, basename="course")
router.register(
    r"enrollments", courses.EnrollmentViewSet, basename="enrollment"
)

# Communication endpoints
router.register(r"chats", chats.ChatRoomViewSet, basename="chat")
router.register(
    r"notifications", views.NotificationViewSet, basename="notification"
)

# System endpoints
router.register(r"statuses", views.StatusViewSet, basename="status")
router.register(
    r"restrictions", 
    courses.CourseStudentRestrictionViewSet, 
    basename="restriction"
)

# =============================================================================
# NESTED ROUTERS - Course-specific endpoints
# =============================================================================
courses_router = NestedDefaultRouter(router, r"courses", lookup="course")

courses_router.register(
    r"lessons", courses.CourseLessonViewSet, basename="course-lessons"
)
courses_router.register(
    r"feedbacks", courses.CourseFeedbackViewSet, basename="course-feedbacks"
)
courses_router.register(
    r"enrollments",
    courses.CourseEnrollmentViewSet,
    basename="course-enrollments",
)

# =============================================================================
# NESTED ROUTERS - Chat-specific endpoints
# =============================================================================
chats_router = NestedDefaultRouter(router, r"chats", lookup="chat_room")
chats_router.register(
    r"participants", chats.ChatParticipantViewSet, basename="chat-participant"
)
chats_router.register(
    r"messages", chats.ChatMessageViewSet, basename="chat-message"
)

# =============================================================================
# URL PATTERNS - Include all router URLs
# =============================================================================
urlpatterns = [
    path("", include(router.urls)),  # Main API endpoints
    path("", include(courses_router.urls)),  # Course-related nested endpoints
    path("", include(chats_router.urls)),  # Chat-related nested endpoints
]
