from django.contrib.auth.models import User
from django.db import models

from courses.models import Course
from lessons.models import Lesson

# Create your models here.

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete= models.CASCADE)
    course = models.ForeignKey(Course, on_delete= models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_enrollment'
            )
        ]

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled")
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(
        max_length=3,
        default="USD"
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )
    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.amount} {self.currency}"

class LessonProgress(models.Model):
    student = models.ForeignKey(User, on_delete= models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete= models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'lesson'],
                                    name='unique_student_lesson_progress')
        ]
