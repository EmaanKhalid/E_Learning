from django.urls import path
from courses import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.course_list, name='course_list'),
    path('course_detail/<int:pk>/', views.course_detail, name='course_detail'),
    path('enroll/<int:pk>/', views.enroll_course, name='enroll_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
]