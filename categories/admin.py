from django.contrib import admin
from .models import Category
from django.urls import path
from django.shortcuts import render
from core.admin import GraphAdmin

class CategoryAdmin(GraphAdmin):
    filter_horizontal = ('experts', 'mechanisms', 'courses', 'builds') 
    list_display = ('title', 'description')
    search_fields = ('title', 'description') 

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('network/<int:object_id>/', self.admin_site.admin_view(self.network_view), name='category_network'),
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



admin.site.register(Category, CategoryAdmin)
