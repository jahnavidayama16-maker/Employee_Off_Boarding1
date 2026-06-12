from django.contrib import admin
from .models import Clearance

class ClearanceAdmin(admin.ModelAdmin):
    list_display = ['department_name', 'resignation', 'status', 'cleared_at']
    list_filter = ['department_name', 'status']
    search_fields = ['resignation__employee__email', 'resignation__employee__full_name']

admin.site.register(Clearance, ClearanceAdmin)
