from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Course(models.Model):
    COURSE_CATEGORIES = [
        ("programming", "Programming"),
        ("data_science", "Data Science"),
        ("web", "Web Development"),
        ("ai", "Artificial Intelligence"),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=COURSE_CATEGORIES)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
