from django.urls import path
from .views import BuildListAPIView,BuildDetailAPIView

urlpatterns = [
    path('', BuildListAPIView.as_view(), name="builds"),
     path('<str:slug>/', BuildDetailAPIView.as_view(), name="build")
]