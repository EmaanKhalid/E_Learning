from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

import stripe

from .models import Payment, Enrollment
# Create your views here.

@login_required
def payment_pending(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        student=request.user
    )

    return render(
        request,
        "enrollments/payment_pending.html",
        {"payment": payment}
    )

@login_required
def payment_history(request):
    payments = Payment.objects.filter(
        student=request.user
    ).select_related("course").order_by("-created_at")

    return render(
        request,
        "enrollments/payment_history.html",
        {"payments": payments}
    )

@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(
            request,
            "Payment session was not found."
        )
        return redirect("course_list")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        checkout_session = stripe.checkout.Session.retrieve(
            session_id
        )

        if checkout_session.payment_status != "paid":
            messages.error(
                request,
                "Payment has not been completed."
            )
            return redirect("course_list")

        payment_id = checkout_session.metadata["payment_id"]

        payment = get_object_or_404(
            Payment,
            id=payment_id,
            student=request.user
        )

        payment.status = "paid"
        payment.payment_reference = checkout_session.id
        payment.save(
            update_fields=[
                "status",
                "payment_reference",
                "updated_at"
            ]
        )

        Enrollment.objects.get_or_create(
            student=request.user,
            course=payment.course
        )

        return render(
            request,
            "enrollments/payment_success.html",
            {
                "payment": payment,
                "session_id": checkout_session.id
            }
        )

    except stripe.error.StripeError:
        messages.error(
            request,
            "Unable to verify your payment with Stripe."
        )
        return redirect("course_list")


@login_required
def payment_cancel(request):
    return render(
        request,
        "enrollments/payment_cancel.html"
    )