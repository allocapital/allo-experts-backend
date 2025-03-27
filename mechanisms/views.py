from django.shortcuts import render
from rest_framework import generics, response, status
from django.db.models import Sum, F, Q
from django.db.models.functions import ExtractYear, ExtractMonth
from collections import defaultdict
from .models import Mechanism, MechanismTrend
from .serializers import MechanismSerializer, TrendItemSerializer

class MechanismListAPIView(generics.ListAPIView):
  serializer_class=MechanismSerializer

  def get_queryset(self):
    return Mechanism.objects.filter(hidden=False)
  

class MechanismDetailAPIView(generics.GenericAPIView):
  serializer_class=MechanismSerializer


  def get(self,requst,slug):
    # md = markdown.Markdown(extensions=["fenced_code"])

    query_set= Mechanism.objects.filter(slug=slug, hidden=False).first()
    # query_set.description=md.convert(query_set.description)

    if query_set:
            serializer = self.serializer_class(query_set)
            return response.Response(serializer.data)
    return response.Response('Not found', status=status.HTTP_404_NOT_FOUND)


def get_quarter_from_month(month):
    """
    Convert a month number (1-12) to a quarter (1-4).
    """
    return (month - 1) // 3 + 1


def format_quarter(year, quarter):
    """
    Format a year and quarter as 'YYYY-Q#'.
    """
    return f"{year}-Q{quarter}"


class TrendsListAPIView(generics.GenericAPIView):
    """
    API endpoint that returns quarterly trend data.
    This is used by the frontend to display the trends chart.
    """
    def get(self, request):
        # Get all trend data
        trends = MechanismTrend.objects.select_related('mechanism').filter(
            Q(mechanism__hidden=False) | Q(mechanism__slug='other')
        )
        
        # Group by mechanism and quarter
        quarterly_data = defaultdict(lambda: defaultdict(float))
        mechanism_info = {}
        
        for trend in trends:
            year = trend.month.year
            month = trend.month.month
            quarter = get_quarter_from_month(month)
            quarter_key = format_quarter(year, quarter)
            
            mechanism_slug = trend.mechanism.slug
            quarterly_data[mechanism_slug][quarter_key] += float(trend.value)
            
            if mechanism_slug not in mechanism_info:
                mechanism_info[mechanism_slug] = {
                    'slug': mechanism_slug,
                    'name': trend.mechanism.title
                }
        
        # Format the data for the frontend
        trend_items = []
        for mechanism_slug, quarters in quarterly_data.items():
            for quarter, value in quarters.items():
                trend_items.append({
                    'quarter': quarter, 
                    'mechanism_slug': mechanism_slug,
                    'mechanism_name': mechanism_info[mechanism_slug]['name'],
                    'value': value
                })
        
        # Sort by quarter and mechanism
        trend_items.sort(key=lambda x: (x['quarter'], x['mechanism_slug']))
        
        serializer = TrendItemSerializer(trend_items, many=True)
        return response.Response(serializer.data)


class MechanismTrendsAPIView(generics.GenericAPIView):
    """
    API endpoint that returns quarterly trend data for a specific mechanism.
    This is used by the frontend to display the mechanism-specific trend chart.
    """
    def get(self, request, slug):
        # Check if the mechanism exists
        mechanism = Mechanism.objects.filter(slug=slug, hidden=False).first()
        if not mechanism:
            return response.Response('Mechanism not found', status=status.HTTP_404_NOT_FOUND)
        
        # Get trend data for the mechanism
        trends = MechanismTrend.objects.filter(mechanism=mechanism)
        
        # Group by quarter
        quarterly_data = defaultdict(float)
        
        for trend in trends:
            year = trend.month.year
            month = trend.month.month
            quarter = get_quarter_from_month(month)
            quarter_key = format_quarter(year, quarter)
            
            quarterly_data[quarter_key] += float(trend.value)
        
        # Format the data for the frontend
        trend_items = []
        for quarter, value in quarterly_data.items():
            trend_items.append({
                'quarter': quarter,  # Using 'quarter' field instead of 'month'
                'mechanism_slug': mechanism.slug,
                'mechanism_name': mechanism.title,
                'value': value
            })
        
        # Sort by quarter
        trend_items.sort(key=lambda x: x['quarter'])
        
        serializer = TrendItemSerializer(trend_items, many=True)
        return response.Response(serializer.data)