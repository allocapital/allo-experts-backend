from django.contrib import admin
from .models import Expert
from django.urls import path
from django.shortcuts import render
from core.admin import GraphAdmin

@admin.register(Expert)
class ExpertModelAdmin(GraphAdmin):
    filter_horizontal = ('mechanisms', 'courses', 'builds', 'experts')
    list_display = ('name', 'description')
    search_fields = ('name',)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["slug"].help_text = "This field is automatically generated"
        return form


    related_object_types = {
        'course': 'courses',
        'mechanism': 'mechanisms',
        'build': 'builds',
    }
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('network/<int:object_id>/', self.admin_site.admin_view(self.network_view), name='expert_network'),
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