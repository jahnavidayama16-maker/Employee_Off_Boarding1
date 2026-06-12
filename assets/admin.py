from django.contrib import admin
from .models import Asset

class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'assigned_to', 'status', 'manager_approval', 'assigned_date']
    list_filter = ['status', 'manager_approval']
    search_fields = ['name', 'assigned_to__email', 'assigned_to__full_name']

admin.site.register(Asset, AssetAdmin)
