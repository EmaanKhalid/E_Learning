from django.urls import path
from lessons import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('<int:pk>/', views.lesson_detail, name='lesson_detail'),
]