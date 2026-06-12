from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_assets, name='manage_assets'),
    path('status/<int:pk>/', views.update_status, name='update_status'),
    path('assign/', views.assign_asset, name='assign_asset'),  # NEW
    path('team/', views.team_assets, name='team_assets'),
    path('manager_approve/<int:pk>/', views.manager_approve_asset, name='manager_approve_asset'),
]
