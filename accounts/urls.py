from django.urls import path
from accounts import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("profile/", views.edit_profile, name="edit_profile"),
    path("email/",views.change_email,name="change_email"),
    path("password/change/",views.change_password,name="change_password"),
    path("connections/",views.account_connections,name="account_connections"),
    path("settings/", views.account_settings, name="account_settings"),
]