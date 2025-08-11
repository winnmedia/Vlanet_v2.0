from .api_urls import urlpatterns as api_patterns

"""
AI   URL 
"""
from django.urls import path
from . import views

app_name = 'video_analysis'

urlpatterns = api_patterns + [
    # Twelve Labs  
    path('analyze/<int:feedback_id>/', views.analyze_feedback_video, name='analyze_video'),
    path('result/<int:feedback_id>/', views.get_analysis_result, name='get_result'),
    path('delete/<int:feedback_id>/', views.delete_analysis, name='delete_analysis'),
    
    # AI  
    path('teacher/<int:feedback_id>/', views.get_teacher_feedback, name='teacher_feedback'),
    path('teachers/', views.get_all_teachers, name='all_teachers'),
    
    #  
    path('search/', views.search_in_videos, name='search_videos'),
]