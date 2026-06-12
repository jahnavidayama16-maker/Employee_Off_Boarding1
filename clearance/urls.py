from django.urls import path
from . import views

urlpatterns = [
    path('', views.clearance_list, name='clearance_list'),
    path('clear/<int:pk>/', views.clear_item, name='clear_item'),
]
