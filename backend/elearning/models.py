from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from elearning.storage import PrivateCourseStorage
import os
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)


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

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default="student"
    )
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


class File(models.Model):
    """Simple file model for course materials"""

    file = models.FileField(
        storage=PrivateCourseStorage(), upload_to="course_materials/%Y/%m/%d"
    )
    original_name = models.CharField(max_length=255)
    is_previewable = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.file and not self.pk:
            self.original_name = self.file.name
            # Simple check for previewable files
            ext = os.path.splitext(self.original_name)[1].lower()
            self.is_previewable = ext in [
                ".jpg",
                ".jpeg",
                ".png",
                ".pdf",
                ".txt",
            ]
        super().save(*args, **kwargs)

    @property
    def mime_type(self):
        ext = os.path.splitext(self.original_name)[1].lower()
        types = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".txt": "text/plain",
        }
        return types.get(ext, "application/octet-stream")


class CourseLesson(models.Model):
    """
    Model for course lessons.
    """

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField(blank=True, null=True)
    file = models.ForeignKey(
        File,
        on_delete=models.SET_NULL,
        related_name="lessons",
        null=True,
        blank=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "course_lessons"
        ordering = ["created_at"]


class CourseFeedback(models.Model):
    """
    Model for course feedback.
    """

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="feedbacks"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="feedbacks",
        null=True,
        blank=True,
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        validators=[
            MinValueValidator(1, "Rating must be at least 1"),
            MaxValueValidator(5, "Rating cannot exceed 5"),
        ],
    )
    text = models.TextField(
        validators=[
            MinLengthValidator(10, "Feedback must be at least 10 characters"),
            MaxLengthValidator(500, "Feedback cannot exceed 500 characters"),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        username = self.user.username if self.user else "Deleted User"
        return f"{username} feedback on {self.course.title}"

    class Meta:
        db_table = "course_feedback"
        unique_together = ("course", "user")
        ordering = ["-created_at"]


class Enrollment(models.Model):
    """
    Model for course enrollments.
    Junction table between User and Course.
    One user can enroll in multiple courses and
    one course can have multiple users.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unenrolled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    class Meta:
        db_table = "enrollments"
        unique_together = ("user", "course")
        ordering = ["-enrolled_at"]
        indexes = [
            # Single compound index covers most queries
            models.Index(fields=["course", "is_active", "enrolled_at"]),
        ]


class Status(models.Model):
    """User status updates that are visible to other users"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="statuses"
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_statuses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}..."


class ChatRoom(models.Model):
    """
    Model for chat between users.
    Chat can be direct, group, or course-wide.
    """

    CHAT_TYPE_CHOICES = [
        ("direct", "Direct"),
        ("group", "Group"),
        ("course", "Course"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + " (" + self.get_chat_type_display() + ")"

    class Meta:
        db_table = "chat_rooms"
        constraints = [
            models.UniqueConstraint(
                fields=["course", "chat_type"],
                condition=models.Q(chat_type="course"),
                name="unique_course_chat_type",
            )
        ]


class ChatMessage(models.Model):
    """
    Model for chat messages.
    """

    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        sender_name = self.sender.username if self.sender else "Deleted User"
        return f"{sender_name} in {self.chat_room.name}"

    class Meta:
        db_table = "chat_messages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["chat_room", "created_at"]),
        ]


class ChatParticipant(models.Model):
    """
    Model for chat participants.
    """

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("participant", "Participant"),
    ]

    chat_room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="participants"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES, default="participant")
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_read_message = models.ForeignKey(
        ChatMessage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="read_by",
    )

    def __str__(self):
        return (
            f"{self.user.username} in {self.chat_room.name}"
            f" ({self.get_role_display()})"
        )

    class Meta:
        db_table = "chat_participants"
        unique_together = ("chat_room", "user")
        ordering = ["-joined_at"]
        indexes = [
            # Only index for active participant filtering
            models.Index(fields=["chat_room", "is_active"]),
        ]


class StudentRestriction(models.Model):
    """
    Model for student restrictions.
    """

    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="restrictions_as_teacher"
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="restrictions_as_student"
    )
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, null=True, blank=True
    )
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.course:
            return (
                f"{self.teacher.username} restricted "
                f"{self.student.username} from {self.course.title}"
            )
        return (
            f"{self.teacher.username} restricted "
            f"{self.student.username} from all courses"
        )

    class Meta:
        unique_together = ["teacher", "student", "course"]
        indexes = [
            models.Index(fields=["student", "teacher"]),
        ]


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_url = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
        ]
