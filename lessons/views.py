from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from lessons.models import Lesson
from enrollments.models import Enrollment

# Create your views here.

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)

    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=lesson.course
    ).exists()

    if not is_enrolled:
        return render(
            request,
            'lessons/access_denied.html',  {'course': lesson.course}
        )

    context = {
        'lesson': lesson
    }

    return render(request, 'lessons/lesson_details.html', context)
