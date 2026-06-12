from django.contrib import admin
from .models import Resignation

class ResignationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'expected_last_day', 'current_stage', 'manager_status', 'hr_status', 'admin_status']
    list_filter = ['current_stage', 'manager_status', 'hr_status', 'admin_status']
    search_fields = ['employee__email', 'employee__full_name', 'reason']

admin.site.register(Resignation, ResignationAdmin)
