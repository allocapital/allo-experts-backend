from django.urls import path
from .views import ExpertListAPIView,ExpertDetailAPIView

urlpatterns = [
    path('', ExpertListAPIView.as_view(), name="experts"),
     path('<str:slug>/', ExpertDetailAPIView.as_view(), name="expert")
]