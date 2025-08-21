from django.contrib import admin
from .models import (
    Course,
    CourseLesson,
    User,
    Enrollment,
    ChatRoom,
    ChatMessage,
    ChatParticipant,
    StudentRestriction,
)

# Register your models here.

# add user model to admin
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ChatParticipant)
admin.site.register(CourseLesson)
admin.site.register(StudentRestriction)
