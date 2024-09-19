from django.contrib import admin
from .models import Mechanism

class MechanismModelAdmin(admin.ModelAdmin):
  list_display = ('title', 'created_at')
  search_fields = ('title', 'description')

admin.site.register(Mechanism, MechanismModelAdmin)

