from django.shortcuts import redirect
from allauth.account.adapter import DefaultAccountAdapter

from .models import EmailOTP
from .utils import create_and_send_otp


class AccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Save the user and create an OTP for email verification.
        """

        user = super().save_user(
            request,
            user,
            form,
            commit=False
        )

        # Keep the account active so Allauth does not send the user
        # to /accounts/inactive/
        user.is_active = True

        if commit:
            user.save()

            # Create and send OTP
            create_and_send_otp(user)

            # Remember the user who needs OTP verification
            request.session["otp_user_id"] = user.pk

        return user

    def pre_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url,
    ):
        """
        Stop users from logging in until their signup OTP
        has been verified.
        """

        try:
            email_otp = EmailOTP.objects.get(user=user)
        except EmailOTP.DoesNotExist:
            email_otp = None

        # If this is a local account with an unverified OTP,
        # redirect to the OTP verification page.
        if email_otp and not email_otp.is_verified:

            request.session["otp_user_id"] = user.pk

            return redirect("verify_otp")

        # Otherwise continue with Allauth's normal login process.
        return super().pre_login(
            request,
            user,
            email_verification=email_verification,
            signal_kwargs=signal_kwargs,
            email=email,
            signup=signup,
            redirect_url=redirect_url,
        )

    def get_signup_redirect_url(self, request):
        """
        Redirect newly registered users to OTP verification.
        """

        return "/accounts/verify-otp/"

    def clean_username(self, username, shallow=False):
        """
        Allow duplicate usernames.

        Allauth still validates the username format and blacklist,
        but database uniqueness is skipped.
        """

        username = (username or "").strip()

        if not username:
            return username

        return super().clean_username(
            username,
            shallow=True
        )