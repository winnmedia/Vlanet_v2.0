"""
System URL Configuration
Includes health checks and monitoring endpoints
"""
from django.urls import path
from . import views
from .health import health_check_view, readiness_check_view, liveness_check_view

app_name = 'system'

urlpatterns = [
    # Health check endpoints (Railway compatible)
    path('health/', health_check_view, name='health_check'),
    path('health/ready/', readiness_check_view, name='readiness_check'),
    path('health/live/', liveness_check_view, name='liveness_check'),
    
    # Legacy health check (backwards compatibility)
    path('health/legacy/', views.health_check, name='health_check_legacy'),
    
    # API 
    path('', views.api_root, name='api_root'),
    
    #  
    path('system/migrations/', views.migration_status, name='migration_status'),
    path('version/', views.version_info, name='version_info'),
    
    # OPTIONS (CORS)
    path('options/', views.options_handler, name='options'),
]