from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from enrollments.models import Enrollment
from allauth.account.forms import ChangePasswordForm
from django.contrib.auth import get_user_model
from .models import EmailOTP
from .utils import create_and_send_otp
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.forms import DisconnectForm


# Create your views here.

User = get_user_model()

@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related("course")

    return render(
        request,
        "accounts/dashboard.html",
        {"enrollments": enrollments}
    )


def verify_otp(request):
    """
    Verify the OTP sent to the user's email.
    """

    user_id = request.session.get("otp_user_id")

    otp_purpose = request.session.get(
        "otp_purpose",
        "signup"
    )

    if not user_id:
        messages.error(
            request,
            "Your verification session has expired. Please register again."
        )
        return redirect("account_signup")

    try:
        user = User.objects.get(id=user_id)
        email_otp = EmailOTP.objects.get(user=user)
    except (User.DoesNotExist, EmailOTP.DoesNotExist):
        messages.error(
            request,
            "Verification information could not be found."
        )
        return redirect("account_signup")

    if request.method == "POST":

        entered_otp = request.POST.get("otp", "").strip()

        if not entered_otp:
            messages.error(
                request,
                "Please enter the verification code."
            )
            return render(
                request,
                "accounts/verify_otp.html",
                {"email": user.email}
            )

        if email_otp.is_expired():
            messages.error(
                request,
                "This verification code has expired. Please request a new one."
            )
            return render(
                request,
                "accounts/verify_otp.html",
                {"email": user.email, "expired": True}
            )

        if entered_otp != email_otp.otp:
            messages.error(
                request,
                "Invalid verification code. Please try again."
            )
            return render(
                request,
                "accounts/verify_otp.html",
                {"email": user.email}
            )

        # ==========================================
        # OTP IS CORRECT
        # ==========================================

        email_otp.is_verified = True
        email_otp.save(update_fields=["is_verified"])

        user.is_active = True
        user.save(update_fields=["is_active"])

        # ==========================================
        # HANDLE EMAIL CHANGE
        # ==========================================

        if otp_purpose == "change_email":

            pending_email = request.session.get("pending_email")

            if not pending_email:
                messages.error(
                    request,
                    "Your email change session has expired. Please try again."
                )
                return redirect("change_email")

            # Check again that the email is still available.
            if User.objects.filter(
                    email__iexact=pending_email
            ).exclude(
                id=user.id
            ).exists():
                request.session.pop("pending_email", None)
                request.session.pop("otp_user_id", None)
                request.session.pop("otp_purpose", None)

                messages.error(
                    request,
                    "This email address is no longer available."
                )
                return redirect("change_email")

            # ==========================================
            # UPDATE USER EMAIL
            # ==========================================

            user.email = pending_email
            user.save(update_fields=["email"])

            # ==========================================
            # UPDATE ALLAUTH EMAIL
            # ==========================================

            EmailAddress.objects.filter(
                user=user
            ).update(
                primary=False
            )

            email_address, created = EmailAddress.objects.update_or_create(
                user=user,
                email=pending_email,
                defaults={
                    "verified": True,
                    "primary": True,
                },
            )

            # ==========================================
            # CLEAN OLD EMAIL RECORDS
            # ==========================================

            EmailAddress.objects.filter(
                user=user
            ).exclude(
                email=pending_email
            ).delete()

            # ==========================================
            # CLEAR SESSION
            # ==========================================

            request.session.pop("pending_email", None)
            request.session.pop("otp_user_id", None)
            request.session.pop("otp_purpose", None)

            messages.success(
                request,
                "Your email address has been changed and verified successfully."
            )

            return redirect("change_email")

        # ==========================================
        # NORMAL SIGNUP OTP VERIFICATION
        # ==========================================

        EmailAddress.objects.filter(
            user=user
        ).update(
            primary=False
        )

        email_address, created = EmailAddress.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={
                "verified": True,
                "primary": True,
            },
        )

        email_address.verified = True
        email_address.primary = True
        email_address.save(
            update_fields=[
                "verified",
                "primary",
            ]
        )

        # Remove signup OTP session information
        request.session.pop("otp_user_id", None)
        request.session.pop("otp_purpose", None)

        messages.success(
            request,
            "Your email has been verified successfully. You can now sign in."
        )

        return redirect("account_login")
        # ==========================================
        # EMAIL CHANGE
        # ==========================================

        if otp_purpose == "change_email":
            request.session.pop("otp_user_id", None)
            request.session.pop("otp_purpose", None)

            messages.success(
                request,
                "Your email address has been changed and verified successfully."
            )

            return redirect("change_email")

        # ==========================================
        # SIGNUP VERIFICATION
        # ==========================================

        request.session.pop("otp_user_id", None)
        request.session.pop("otp_purpose", None)

        messages.success(
            request,
            "Your email has been verified successfully. You can now sign in."
        )

        return redirect("account_login")

    return render(
        request,
        "accounts/verify_otp.html",
        {"email": user.email}
    )

def resend_otp(request):
    """
    Generate and send a new OTP.

    For email changes, send the OTP to the pending new email.
    For signup verification, send it to the user's current email.
    """

    user_id = request.session.get("otp_user_id")

    if not user_id:
        messages.error(
            request,
            "Your verification session has expired. Please register again."
        )
        return redirect("account_signup")

    try:
        user = User.objects.get(id=user_id)
        email_otp = EmailOTP.objects.get(user=user)
    except (User.DoesNotExist, EmailOTP.DoesNotExist):
        messages.error(
            request,
            "Verification information could not be found."
        )
        return redirect("account_signup")

    # Already verified
    if email_otp.is_verified:
        if request.session.get("otp_purpose") == "change_email":
            return redirect("change_email")

        return redirect("account_login")

    # Check whether this OTP is for changing email
    otp_purpose = request.session.get(
        "otp_purpose",
        "signup"
    )

    if otp_purpose == "change_email":

        pending_email = request.session.get("pending_email")

        if not pending_email:
            messages.error(
                request,
                "Your email change session has expired. Please try again."
            )
            return redirect("change_email")

        create_and_send_otp(
            user,
            recipient_email=pending_email
        )

    else:
        create_and_send_otp(user)

    messages.success(
        request,
        "A new verification code has been sent to your email."
    )

    return redirect("verify_otp")

@login_required
def edit_profile(request):
    """
    Allow the logged-in user to edit their profile information.
    """

    user = request.user

    if request.method == "POST":
        user.username = request.POST.get("username", "").strip()
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()

        if not user.username:
            messages.error(request, "Username is required.")
        else:
            user.save(
                update_fields=[
                    "username",
                    "first_name",
                    "last_name",
                ]
            )

            messages.success(
                request,
                "Your profile has been updated successfully."
            )

            return redirect("edit_profile")

    return render(
        request,
        "account/edit_profile.html",
        {
            "user": user,
        }
    )

@login_required
def change_email(request):
    """
    Start the email-change process.

    The new email is stored temporarily in the session.
    The actual account email changes only after OTP verification.
    """

    user = request.user

    if request.method == "POST":

        new_email = request.POST.get("email", "").strip().lower()

        if not new_email:
            messages.error(
                request,
                "Please enter a new email address."
            )

        elif new_email == user.email.lower():
            messages.error(
                request,
                "This is already your current email address."
            )

        elif User.objects.filter(
            email__iexact=new_email
        ).exclude(
            id=user.id
        ).exists():
            messages.error(
                request,
                "This email address is already in use."
            )

        else:
            # Store the new email temporarily.
            request.session["pending_email"] = new_email
            request.session["otp_user_id"] = user.pk
            request.session["otp_purpose"] = "change_email"

            # Generate and send OTP directly to the new email.
            create_and_send_otp(
                user,
                recipient_email=new_email
            )

            messages.success(
                request,
                "A verification code has been sent to your new email address."
            )

            return redirect("verify_otp")

    return render(
        request,
        "account/email.html",
        {
            "user": user,
        }
    )

@login_required
def change_password(request):
    """
    Allow the logged-in user to change their password.
    """

    if request.method == "POST":
        form = ChangePasswordForm(
            user=request.user,
            data=request.POST
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your password has been changed successfully."
            )

            return redirect("change_password")

    else:
        form = ChangePasswordForm(
            user=request.user
        )

    return render(
        request,
        "account/password_change.html",
        {
            "form": form,
        }
    )

@login_required
def account_connections(request):
    """
    Display and manage the social accounts connected
    to the logged-in user.
    """

    if request.method == "POST":

        form = DisconnectForm(
            request=request,
            data=request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your Google account has been disconnected successfully."
            )

            return redirect("account_connections")

    else:

        form = DisconnectForm(
            request=request
        )

    google_account = SocialAccount.objects.filter(
        user=request.user,
        provider="google"
    ).first()

    return render(
        request,
        "socialaccount/account_connections.html",
        {
            "google_account": google_account,
            "form": form
        }
    )

@login_required
def account_settings(request):
    return render(request, "account/settings.html")