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
