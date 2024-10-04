from django.urls import path
from .views import CourseListAPIView,CourseDetailAPIView

urlpatterns = [
    path('', CourseListAPIView.as_view(), name="courses"),
    path('<str:slug>/', CourseDetailAPIView.as_view(), name="course")
]