from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from enrollments.models import Enrollment

# Create your views here.

import re

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from enrollments.models import Enrollment


# Create your views here.

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if len(password) < 8:

            messages.error(
                request,
                'Password must be at least 8 characters long.'
            )

            return render(
                request,
                'accounts/register.html'
            )

        if not re.search(r'[^A-Za-z0-9]', password):

            messages.error(
                request,
                'Password must contain at least one special character.'
            )

            return render(
                request,
                'accounts/register.html'
            )

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return render(
                request,
                'accounts/register.html'
            )


        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                'Username already exists.'
            )

            return render(
                request,
                'accounts/register.html'
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            'Account created successfully. You can now login.'
        )

        return redirect('login')

    return render(
        request,
        'accounts/register.html'
    )

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            if next_url:
                return redirect(next_url)

            return redirect('dashboard')

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(
        student=request.user
    )

    context = {
        'enrollments': enrollments
    }

    return render(
        request,
        'accounts/dashboard.html',
        context
    )
