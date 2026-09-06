from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Course
from enrollments.models import Enrollment
from lessons.models import Lesson

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

    if request.method == 'POST':
        if Enrollment.objects.filter(
                student=student,
                course=course
        ).exists():
            return HttpResponse("Already enrolled")

        Enrollment.objects.create(
            student=student,
            course=course
        )

        return redirect('course_detail', pk=course.pk)

    return redirect('course_detail', pk=course.pk)

@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    context = {'enrollments': enrollments}
    return render(request, 'courses/my_courses.html', context)