from rest_framework import serializers
from .models import Mechanism
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
