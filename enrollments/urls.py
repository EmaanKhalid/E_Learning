from django.urls import path
from enrollments import views


urlpatterns = [
    path(
        "payment/<int:payment_id>/",
        views.payment_pending,
        name="payment_pending"
    ),
path(
    "payments/",
    views.payment_history,
    name="payment_history"
),
path(
    "payment/success/",
    views.payment_success,
    name="payment_success"
),
path(
    "payment/cancel/",
    views.payment_cancel,
    name="payment_cancel"
),
]
