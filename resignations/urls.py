from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.request_resignation, name='request_resignation'),
    path('approvals/', views.team_approvals, name='team_approvals'),
    path('approve/<int:pk>/<str:role>/', views.approve_resignation, name='approve_resignation'),
    path('feedback/<int:pk>/', views.submit_exit_feedback, name='submit_exit_feedback'),
]
