"""
  URL 
"""
from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    # 
    path('health/', views.health_check, name='health_check'),
    
    # API 
    path('', views.api_root, name='api_root'),
    
    #  
    path('system/migrations/', views.migration_status, name='migration_status'),
    path('version/', views.version_info, name='version_info'),
    
    # OPTIONS (CORS)
    path('options/', views.options_handler, name='options'),
]