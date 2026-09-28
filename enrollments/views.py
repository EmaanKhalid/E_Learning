from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import EmailMultiAlternatives
import stripe
from decimal import Decimal
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
def payment_receipt(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related("course", "student"),
        id=payment_id,
        student=request.user,
        status="paid"
    )

    return render(
        request,
        "enrollments/payment_receipt.html",
        {
            "payment": payment
        }
    )

@login_required
def payment_invoice(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related("course", "student"),
        id=payment_id,
        student=request.user,
        status="paid"
    )

    return render(
        request,
        "enrollments/payment_invoice.html",
        {
            "payment": payment
        }
    )


def send_invoice_email(payment):
    subject = f"Invoice for {payment.course.title}"

    student_name = payment.student.get_full_name() or payment.student.username

    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 700px; margin: auto; padding: 30px; border: 1px solid #ddd;">

            <h2 style="color: #0d6efd;">E-Learning Website</h2>
            <p>Dear <strong>{student_name}</strong>,</p>

            <p>
                Thank you for your purchase. Your payment has been successfully
                received.
            </p>

            <hr>

            <h3>Invoice</h3>

            <p>
                <strong>Invoice No:</strong>
                INV-{payment.id:06d}
            </p>

            <p>
                <strong>Course:</strong>
                {payment.course.title}
            </p>

            <p>
                <strong>Amount:</strong>
                {payment.currency.upper()} {payment.amount}
            </p>

            <p>
                <strong>Payment Status:</strong>
                <span style="color: green;">PAID</span>
            </p>

            <p>
                <strong>Payment Reference:</strong>
                {payment.payment_reference or "N/A"}
            </p>

            <p>
                <strong>Payment Date:</strong>
                {payment.created_at.strftime("%B %d, %Y")}
            </p>

            <hr>

            <h3>
                Total:
                {payment.currency.upper()} {payment.amount}
            </h3>

            <p style="color: #666;">
                Thank you for choosing E-Learning Website.
            </p>

        </div>
    </body>
    </html>
    """

    text_message = f"""
E-Learning Website

Dear {student_name},

Thank you for your purchase. Your payment has been successfully received.

Invoice No: INV-{payment.id:06d}
Course: {payment.course.title}
Amount: {payment.currency.upper()} {payment.amount}
Payment Status: PAID
Payment Reference: {payment.payment_reference or "N/A"}
Payment Date: {payment.created_at.strftime("%B %d, %Y")}

Total: {payment.currency.upper()} {payment.amount}

Thank you for choosing E-Learning Website.
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=None,
        to=[payment.student.email]
    )

    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)

def send_enrollment_confirmation_email(payment):
    subject = f"Course Enrollment Confirmation - {payment.course.title}"

    student_name = (
        payment.student.get_full_name()
        or payment.student.username
    )

    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 700px; margin: auto; padding: 30px;
                    border: 1px solid #ddd; border-radius: 8px;">

            <h2 style="color: #0d6efd;">
                E-Learning Website
            </h2>

            <h3>Course Enrollment Confirmed</h3>

            <p>
                Dear <strong>{student_name}</strong>,
            </p>

            <p>
                Your enrollment has been successfully confirmed.
            </p>

            <div style="background: #f8f9fa; padding: 20px;
                        border-radius: 6px; margin: 20px 0;">

                <p>
                    <strong>Course:</strong>
                    {payment.course.title}
                </p>

                <p>
                    <strong>Enrollment Date:</strong>
                    {payment.created_at.strftime("%B %d, %Y")}
                </p>

                <p>
                    <strong>Payment Status:</strong>
                    <span style="color: green;">
                        PAID
                    </span>
                </p>

            </div>

            <p>
                You can now access your course from your
                E-Learning dashboard.
            </p>

            <p>
                Thank you for choosing E-Learning Website.
            </p>

            <hr>

            <p style="color: #777; font-size: 13px;">
                This is an automated enrollment confirmation email.
            </p>

        </div>
    </body>
    </html>
    """

    text_message = f"""
E-Learning Website

Course Enrollment Confirmed

Dear {student_name},

Your enrollment has been successfully confirmed.

Course: {payment.course.title}
Enrollment Date: {payment.created_at.strftime("%B %d, %Y")}
Payment Status: PAID

You can now access your course from your E-Learning dashboard.

Thank you for choosing E-Learning Website.
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=None,
        to=[payment.student.email]
    )

    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)

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
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status != "paid":
            messages.error(
                request,
                "Payment has not been completed."
            )
            return redirect("course_list")

        course_id = checkout_session.metadata["course_id"]

        if not course_id:
            messages.error(
                request,
                "Course information was not found."
            )
            return redirect("course_list")

        payment = Payment.objects.filter(
            student=request.user,
            course_id=course_id,
            payment_reference=checkout_session.id
        ).first()

        was_already_paid = payment is not None

        if not payment:
            payment = Payment.objects.create(
                student=request.user,
                course_id=course_id,
                amount=Decimal(checkout_session.amount_total) / Decimal("100"),
                currency="USD",
                status="paid",
                payment_reference=checkout_session.id
            )

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course_id=course_id
        )

        if not was_already_paid:
            try:
                send_enrollment_confirmation_email(payment)
            except Exception:
                messages.warning(
                    request,
                    "Enrollment was successful, but the confirmation email could not be sent."
                )

            try:
                send_invoice_email(payment)
            except Exception:
                messages.warning(
                    request,
                    "Payment was successful, but the invoice email could not be sent."
                )

        if not was_already_paid:
            try:
                send_invoice_email(payment)
            except Exception:
                messages.warning(
                    request,
                    "Payment was successful, but the invoice email could not be sent."
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