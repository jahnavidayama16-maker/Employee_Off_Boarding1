from django.contrib import admin
from .models import AuditLog

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action']
    list_filter = ['timestamp']
    search_fields = ['action', 'user__email', 'user__full_name']

admin.site.register(AuditLog, AuditLogAdmin)
