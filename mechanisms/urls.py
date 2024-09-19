from django.urls import path
from .views import MechanismListAPIView,MechanismDetailAPIView

urlpatterns = [
    path('mechanisms', MechanismListAPIView.as_view(), name="mechanisms"),
     path('mechanisms/<str:slug>', MechanismDetailAPIView.as_view(), name="mechanism")
]