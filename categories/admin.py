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
            path('network-data/<int:object_id>/', self.admin_site.admin_view(self.graph_data_view), name='category_network_data'),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        context = self.get_graph_view_context(request, object_id)
        if context:
            extra_context.update(context)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)



admin.site.register(Category, CategoryAdmin)
