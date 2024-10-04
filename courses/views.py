from django.shortcuts import render
from rest_framework import generics,response,status
from .models import Course
from .serializers import CourseSerializer

class CourseListAPIView(generics.ListAPIView):
  serializer_class=CourseSerializer

  def get_queryset(self):
    print("Goodbye cruel world!")
    return Course.objects.all()
  

class CourseDetailAPIView(generics.GenericAPIView):
  serializer_class=CourseSerializer


  def get(self,requst,slug):

    query_set= Course.objects.filter(slug=slug).first()

    if query_set:
      return response.Response(self.serializer_class(query_set).data)
    return response.Response('Not found', status=status.HTTP_404_NOT_FOUND)