from django.contrib import admin
from .models import Mechanism

class MechanismModelAdmin(admin.ModelAdmin):
  list_display = ('title', 'created_at', 'slug')
  search_fields = ('title', 'description', 'slug')

admin.site.register(Mechanism, MechanismModelAdmin)

