from django.contrib import admin
from .models import Build
from django.urls import path
from django.shortcuts import render
from core.admin import GraphAdmin
class BuildModelAdmin(GraphAdmin):
  filter_horizontal = ('mechanisms', 'courses', 'experts')

  def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["slug"].help_text = "This field is automatically generated"
        return form
  
  list_display = ('title', 'created_at', 'slug')
  search_fields = ('title', 'description', 'slug')


  related_object_types = {
        'course': 'courses',
        'mechanism': 'mechanisms',
        'expert': 'experts',
    }
  def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('network/<int:object_id>/', self.admin_site.admin_view(self.network_view), name='build_network'),
        ]
        return custom_urls + urls

  def network_view(self, request, object_id):
        instance = self.get_object(request, object_id)
        related_data = self.get_related_data(instance)
        return render(request, 'core/change_form.html', {
            'data': related_data,
            'original': instance,
            'graph_script': self.get_graph_script(related_data),
        })
  
admin.site.register(Build, BuildModelAdmin)

