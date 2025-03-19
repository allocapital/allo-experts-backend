from django.urls import path
from .views import (
    MechanismListAPIView,
    MechanismDetailAPIView,
    TrendsListAPIView,
    MechanismTrendsAPIView
)

urlpatterns = [
    path('', MechanismListAPIView.as_view(), name="mechanisms"),
    path('trends/', TrendsListAPIView.as_view(), name="trends"),
    path('trends/<str:slug>/', MechanismTrendsAPIView.as_view(), name="mechanism_trends"),
    path('<str:slug>/', MechanismDetailAPIView.as_view(), name="mechanism"),
]