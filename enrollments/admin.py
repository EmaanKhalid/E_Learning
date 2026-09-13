from django.contrib import admin
from .models import Enrollment, LessonProgress,Payment

# Register your models here.
admin.site.register(Enrollment)
admin.site.register(LessonProgress)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "amount",
        "currency",
        "status",
        "payment_reference",
        "created_at"
    )

    list_filter = (
        "status",
        "currency",
        "created_at"
    )

    search_fields = (
        "student__username",
        "student__email",
        "course__title",
        "payment_reference"
    )

    readonly_fields = (
        "created_at",
        "updated_at"
    )
