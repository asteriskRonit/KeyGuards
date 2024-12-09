from django.contrib import admin
from .models import User_Admin
from .models import UserTab
from .models import Department
from .models import RegisterFace

# Register your model here
admin.site.register(User_Admin)
admin.site.register(UserTab)
admin.site.register(Department)
admin.site.register(RegisterFace)