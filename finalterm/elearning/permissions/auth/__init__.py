"""
Authentication-related permissions for the eLearning platform.

This package contains permission classes that control access to authentication
functionality such as user registration, login, and logout.
"""

from .auth_permissions import IsTeacher, IsTeacherOrAdmin, IsStudent

__all__ = [
    'IsTeacher',
    'IsTeacherOrAdmin', 
    'IsStudent',
]
