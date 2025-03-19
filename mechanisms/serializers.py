from rest_framework import serializers
from .models import Mechanism, MechanismTrend, MechanismMapping
from experts.models import Expert
from courses.models import Course
from builds.models import Build

class ExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expert
        fields = ("id", "name", "slug", "description", "expert_in", "contact_info_telegram", "contact_info_twitter", "contact_info_email", "avatar")

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id",
            "title",
            "description",
            "slug",
            "background_img",
            "background_color",
            "starts_at",
            "register_url") 

class BuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Build
        fields = ("title", "description", "slug", "status", "type", "background_img", "background_color")

class MechanismSerializer(serializers.ModelSerializer):
    related_experts = ExpertSerializer(many=True, read_only=True, source='experts')  # Use the related_name from ManyToMany field
    related_courses = CourseSerializer(many=True, read_only=True, source='courses')  # Use the related_name from ManyToMany field
    related_builds = BuildSerializer(many=True, read_only=True, source='builds')  # Use the related_name from ManyToMany field

    class Meta: 
        model = Mechanism
        fields = "__all__"


class MechanismMappingSerializer(serializers.ModelSerializer):
    mechanism_name = serializers.CharField(source='mechanism.title', read_only=True)
    mechanism_slug = serializers.CharField(source='mechanism.slug', read_only=True)
    
    class Meta:
        model = MechanismMapping
        fields = ('id', 'funder', 'grant_pool_name', 'mechanism', 'mechanism_name', 'mechanism_slug', 'priority')


class MechanismTrendSerializer(serializers.ModelSerializer):
    mechanism_name = serializers.CharField(source='mechanism.title', read_only=True)
    mechanism_slug = serializers.CharField(source='mechanism.slug', read_only=True)
    month = serializers.DateField(format="%Y-%m")
    
    class Meta:
        model = MechanismTrend
        fields = ('id', 'mechanism', 'mechanism_name', 'mechanism_slug', 'month', 'value')


class TrendItemSerializer(serializers.Serializer):
    """
    Serializer for the frontend TrendItem format.
    """
    quarter = serializers.CharField()  # Format: "YYYY-Q#"
    mechanism_slug = serializers.CharField()
    mechanism_name = serializers.CharField()
    value = serializers.FloatField()
