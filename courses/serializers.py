from rest_framework import serializers
from .models import Course
from mechanisms.models import Mechanism
from builds.models import Build
from experts.models import Expert

class MechanismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mechanism
        fields = ("title", "slug", "background_img", "background_color")

class BuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Build
        fields = ("title", "slug", "status", "type", "background_img", "background_color")
class ExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expert
        fields = ("id", "name", "slug", "expert_in", "contact_info_telegram", "contact_info_twitter", "contact_info_email", "avatar")



class CourseSerializer(serializers.ModelSerializer):
   related_mechanisms = MechanismSerializer(many=True, read_only=True, source='mechanisms')  # Use the related_name from ManyToMany field
   related_builds = BuildSerializer(many=True, read_only=True, source='builds')  # Use the related_name from ManyToMany field
   related_experts = ExpertSerializer(many=True, read_only=True, source='experts')  # Use the related_name from ManyToMany field

   class Meta: 
      model=Course
      fields="__all__"

