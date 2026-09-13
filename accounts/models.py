from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class EmailOTP(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_otp'
    )

    otp = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    is_verified = models.BooleanField(
        default=False
    )

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.otp}"