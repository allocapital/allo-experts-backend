from django.contrib import admin
from .models import Expert

@admin.register(Expert)
class ExpertModelAdmin(admin.ModelAdmin):
    filter_horizontal = ('mechanisms', 'courses', 'builds')
    list_display = ('name', 'description')
    search_fields = ('name',)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["slug"].help_text = "This field is automatically generated"
        return form
