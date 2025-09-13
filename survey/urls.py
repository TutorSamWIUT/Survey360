"""URL configuration for survey app."""

from django.urls import path
from . import views

urlpatterns = [
    # Admin routes (custom interface)
    path('admin/', views.admin_login_view, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/surveys/', views.survey_list_view, name='survey_list'),
    path('admin/surveys/create/', views.create_survey_view, name='create_survey'),
    path('admin/surveys/<int:survey_id>/', views.survey_detail_view, name='survey_detail'),
    path('admin/surveys/<int:survey_id>/generate-report/', views.generate_report_view, name='generate_report'),
    path('admin/surveys/<int:survey_id>/send-report/', views.send_report_view, name='send_report'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),
    
    # Survey routes
    path('survey/leader/<str:token>/', views.leader_self_assessment_view, name='leader_self_assessment'),
    path('survey/leader/<str:token>/dashboard/', views.leader_dashboard_view, name='leader_dashboard'),
    path('survey/<str:token>/', views.participant_survey_view, name='participant_survey'),
    path('survey/<str:token>/submit/', views.submit_survey_view, name='submit_survey'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    
    # Report routes
    path('report/<str:report_token>/', views.view_report, name='view_report'),
    
    # API endpoints
    path('api/survey/<str:token>/submit/', views.api_submit_survey, name='api_submit'),
    path('api/admin/generate-report/<int:survey_id>/', views.api_generate_report, name='api_generate_report'),
]