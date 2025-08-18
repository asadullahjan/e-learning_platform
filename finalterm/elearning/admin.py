from django.contrib import admin
from .models import (
    Course,
    User,
    Enrollment,
    ChatRoom,
    ChatMessage,
    ChatParticipant,
)

# Register your models here.

# add user model to admin
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ChatParticipant)
