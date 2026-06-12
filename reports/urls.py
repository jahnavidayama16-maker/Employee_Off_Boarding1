from django.urls import path
from . import views

urlpatterns = [
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('audit-log/', views.audit_log, name='audit_log'),
]
