from rest_framework import serializers
from .models import Build
from mechanisms.models import Mechanism
from courses.models import Course
from experts.models import Expert

class MechanismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mechanism
        fields = ("title", "slug", "background_img", "background_color")

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id",
            "title",
            "slug",
            "background_img",
            "background_color",
            "starts_at",
            "register_url") 

class ExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expert
        fields = ("id", "name", "slug", "expert_in", "contact_info_telegram", "contact_info_twitter", "contact_info_email", "avatar")


class BuildSerializer(serializers.ModelSerializer):
   related_mechanisms = MechanismSerializer(many=True, read_only=True, source='mechanisms')  # Use the related_name from ManyToMany field
   related_courses = CourseSerializer(many=True, read_only=True, source='courses')  # Use the related_name from ManyToMany field
   related_experts = ExpertSerializer(many=True, read_only=True, source='experts')  # Use the related_name from ManyToMany field

   class Meta: 
      model=Build
      fields="__all__"

