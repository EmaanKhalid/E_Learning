from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course
from enrollments.models import Enrollment, Payment
from lessons.models import Lesson
from django.conf import settings
from decimal import Decimal
import stripe

# Create your views here.

def course_list(request):
    courses = Course.objects.all()
    context = {'courses': courses}
    print(request.user.is_authenticated)
    return render(request, 'courses/course_list.html', context)

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = Lesson.objects.filter(course=course)

    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists()

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled
    }

    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    student = request.user

    if Enrollment.objects.filter(
        student=student,
        course=course
    ).exists():
        messages.warning(
            request,
            "You are already enrolled in this course."
        )
        return redirect("course_detail", pk=pk)

    payment = Payment.objects.filter(
        student=student,
        course=course,
        status="pending"
    ).first()

    if payment:
        messages.warning(
            request,
            "You already have a pending payment for this course."
        )
        return redirect("course_detail", pk=pk)

    payment = Payment.objects.create(
        student=student,
        course=course,
        amount=course.price,
        currency="USD",
        status="pending"
    )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": course.title
                    },
                    "unit_amount": int(
                        Decimal(course.price) * Decimal("100")
                    )
                },
                "quantity": 1
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(
            "/enrollments/payment/success/"
        ) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(
            "/enrollments/payment/cancel/"
        ),
        metadata={
            "payment_id": str(payment.id),
            "course_id": str(course.id),
            "student_id": str(student.id)
        }
    )

    payment.payment_reference = checkout_session.id
    payment.save(update_fields=["payment_reference"])

    return redirect(checkout_session.url)
@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    context = {'enrollments': enrollments}
    return render(request, 'courses/my_courses.html', context)