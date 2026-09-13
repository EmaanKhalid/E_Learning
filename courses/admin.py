from django.contrib import admin
from .models import Course


# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "instructor",
        "price",
        "duration",
        "created_at"
    )
    list_filter = (
        "category",
        "instructor"
    )
    search_fields = (
        "title",
        "description"
    )