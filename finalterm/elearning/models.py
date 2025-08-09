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


class Course(models.Model):
    """
    Model for courses.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courses_taught"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "courses"
        ordering = ["-created_at"]


class Enrollment(models.Model):
    """
    Model for course enrollments.
    Junction table between User and Course.
    One user can enroll in multiple courses and
    one course can have multiple users.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unenrolled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    class Meta:
        db_table = "enrollments"
        unique_together = ("user", "course")
        ordering = ["-enrolled_at"]
