from django.contrib import admin
from .models import Enrollment, LessonProgress

# Register your models here.
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
