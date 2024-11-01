from rest_framework import serializers
from .models import Expert
from mechanisms.models import Mechanism
from courses.models import Course
from builds.models import Build

class MechanismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mechanism
        fields = ("title", "slug", "background_img", "background_color")

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


class ExpertSerializer(serializers.ModelSerializer):
   related_mechanisms = MechanismSerializer(many=True, read_only=True, source='mechanisms')  # Use the related_name from ManyToMany field
   related_courses = CourseSerializer(many=True, read_only=True, source='courses')  # Use the related_name from ManyToMany field
   related_builds = BuildSerializer(many=True, read_only=True, source='builds')  # Use the related_name from ManyToMany field

   class Meta: 
      model=Expert
      fields="__all__"

