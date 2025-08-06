from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with essential fields for eLearning platform.
    Supports both Student and Teacher user types.
    """

    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
    ]

    # Override email field to make it unique
    email = models.EmailField(unique=True)
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        db_table = "users"
