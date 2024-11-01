from django.shortcuts import render
from rest_framework import generics,response,status
from .models import Expert
from .serializers import ExpertSerializer


class ExpertListAPIView(generics.ListAPIView):
  serializer_class=ExpertSerializer

  def get_queryset(self):
    return Expert.objects.filter(hidden=False)
  

class ExpertDetailAPIView(generics.GenericAPIView):
  serializer_class=ExpertSerializer


  def get(self,requst,slug):
    query_set= Expert.objects.filter(slug=slug, hidden=False).first()

    if query_set:
            serializer = self.serializer_class(query_set)
            return response.Response(serializer.data)
    return response.Response('Not found', status=status.HTTP_404_NOT_FOUND)