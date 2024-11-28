from django.contrib import admin
from .models import Build
from django.urls import path
from django.shortcuts import render
from core.admin import GraphAdmin
from django.utils.html import format_html

class BuildModelAdmin(GraphAdmin):
  filter_horizontal = ('mechanisms', 'courses', 'experts', 'builds', 'categories')

  def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["slug"].help_text = "This field is automatically generated"
        return form
  
  list_display = ('title', 'created_at', 'slug', 'view_on_site_link')
  search_fields = ('title', 'description', 'slug')

  def view_on_site_link(self, obj):
        return format_html('<a href="{}" target="_blank">View on allo.expert</a>', obj.get_absolute_url())
  view_on_site_link.short_description = 'allo.expert link'

  def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('network/<int:object_id>/', self.admin_site.admin_view(self.network_view), name='build_network'),
            path('network-data/<int:object_id>/', self.admin_site.admin_view(self.graph_data_view), name='build_network_data'),
        ]
        return custom_urls + urls

  def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        context = self.get_graph_view_context(request, object_id)
        if context:
            extra_context.update(context)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
  
admin.site.register(Build, BuildModelAdmin)

