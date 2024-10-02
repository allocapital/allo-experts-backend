from django.urls import path
from .views import MechanismListAPIView,MechanismDetailAPIView

urlpatterns = [
    path('', MechanismListAPIView.as_view(), name="mechanisms"),
     path('<str:slug>/', MechanismDetailAPIView.as_view(), name="mechanism")
]