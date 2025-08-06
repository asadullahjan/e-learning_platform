from django.contrib import admin
from .models import User

# Register your models here.

# add user model to admin
admin.site.register(User)
