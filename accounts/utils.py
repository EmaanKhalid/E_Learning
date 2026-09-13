import secrets
from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailOTP


OTP_EXPIRY_MINUTES = 10


def generate_otp():
    """
    Generate a secure 6-digit OTP.
    """
    return f"{secrets.randbelow(1000000):06d}"


def create_and_send_otp(user, recipient_email=None):
    """
    Create a new OTP for the user and send it by email.

    If recipient_email is provided, the OTP is sent there.
    Otherwise, it is sent to the user's current email.
    """

    otp = generate_otp()

    expires_at = timezone.now() + timedelta(
        minutes=OTP_EXPIRY_MINUTES
    )

    email_otp, created = EmailOTP.objects.update_or_create(
        user=user,
        defaults={
            "otp": otp,
            "expires_at": expires_at,
            "is_verified": False,
        }
    )

    send_mail(
        subject="Verify your E-Learning account",
        message=(
            f"Hello {user.username},\n\n"
            f"Your verification code is: {otp}\n\n"
            f"This code will expire in {OTP_EXPIRY_MINUTES} minutes.\n\n"
            f"If you did not request this change, you can safely ignore "
            f"this email."
        ),
        from_email=None,
        recipient_list=[
            recipient_email or user.email
        ],
        fail_silently=False,
    )

    return email_otp