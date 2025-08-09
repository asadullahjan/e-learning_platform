from django.contrib import admin
from .models import Course, User

# Register your models here.

# add user model to admin
admin.site.register(User)
admin.site.register(Course)
