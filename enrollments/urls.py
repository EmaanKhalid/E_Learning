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
    "payment/<int:payment_id>/receipt/",
    views.payment_receipt,
    name="payment_receipt"
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
path(
    "payment/<int:payment_id>/invoice/",
    views.payment_invoice,
    name="payment_invoice"
),
]
