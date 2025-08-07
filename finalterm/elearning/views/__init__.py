# Import all views for easy access
from .auth_views import register, login_view, logout_view
from .users import user_profile, update_profile
from .courses.course_views import CourseViewSet

__all__ = [
    "register",
    "login_view",
    "logout_view",
    "user_profile",
    "update_profile",
    "CourseViewSet",
]
