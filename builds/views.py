from django.shortcuts import render
from rest_framework import generics,response,status
from .models import Build
from .serializers import BuildSerializer

class BuildListAPIView(generics.ListAPIView):
  serializer_class=BuildSerializer

  def get_queryset(self):
    return Build.objects.filter(hidden=False)
  

class BuildDetailAPIView(generics.GenericAPIView):
  serializer_class=BuildSerializer


  def get(self,requst,slug):
    # md = markdown.Markdown(extensions=["fenced_code"])

    query_set= Build.objects.filter(slug=slug, hidden=False).first()
    # query_set.description=md.convert(query_set.description)

    if query_set:
      return response.Response(self.serializer_class(query_set).data)
    return response.Response('Not found', status=status.HTTP_404_NOT_FOUND)