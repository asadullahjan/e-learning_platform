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


class ChatParticipant(models.Model):
    """
    Model for chat participants.
    """

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("participant", "Participant"),
    ]

    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES, default="participant")
    joined_at = models.DateTimeField(auto_now_add=True)
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
