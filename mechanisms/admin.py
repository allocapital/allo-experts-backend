from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Mechanism, MechanismMapping, MechanismTrend
from core.admin import GraphAdmin
from django.utils.html import format_html

class MechanismAdmin(GraphAdmin):
    filter_horizontal = ('experts', 'builds', 'courses', 'mechanisms', 'categories')

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
            path('network/<int:object_id>/', self.admin_site.admin_view(self.network_view), name='mechanism_network'),
            path('network-data/<int:object_id>/', self.admin_site.admin_view(self.graph_data_view), name='mechanism_network_data'),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        context = self.get_graph_view_context(request, object_id)
        if context:
            extra_context.update(context)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


class MechanismMappingAdmin(admin.ModelAdmin):
    list_display = ('funder', 'grant_pool_name', 'mechanism', 'priority')
    list_filter = ('mechanism', 'funder')
    search_fields = ('funder', 'grant_pool_name', 'mechanism__title')
    autocomplete_fields = ('mechanism',)
    ordering = ('-priority', 'funder', 'grant_pool_name')


class MechanismTrendAdmin(admin.ModelAdmin):
    list_display = ('mechanism', 'month', 'value', 'created_at', 'updated_at')
    list_filter = ('mechanism', 'month')
    search_fields = ('mechanism__title',)
    autocomplete_fields = ('mechanism',)
    ordering = ('-month', 'mechanism')
    date_hierarchy = 'month'
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Mechanism, MechanismAdmin)
admin.site.register(MechanismMapping, MechanismMappingAdmin)
admin.site.register(MechanismTrend, MechanismTrendAdmin)
