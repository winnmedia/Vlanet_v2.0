"""
Video Analysis URL Configuration
Consolidated module to prevent import errors in production
"""
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from . import views

app_name = 'video_analysis'

# API View Functions (previously in api_urls.py)
@api_view(['GET'])
def analysis_list(request):
    """비디오 분석 목록 API"""
    return Response({"analyses": [], "count": 0})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_video_api(request):
    """비디오 분석 시작 API"""
    return Response({"message": "Analysis endpoint ready", "status": "ok"})

# Combined URL patterns
urlpatterns = [
    # API endpoints (previously from api_urls.py)
    path('', analysis_list, name='analysis_list'),
    path('api/analyze/', analyze_video_api, name='analyze_video_api'),
    
    # Twelve Labs endpoints
    path('analyze/<int:feedback_id>/', views.analyze_feedback_video, name='analyze_video'),
    path('result/<int:feedback_id>/', views.get_analysis_result, name='get_result'),
    path('delete/<int:feedback_id>/', views.delete_analysis, name='delete_analysis'),
    
    # AI Teacher endpoints
    path('teacher/<int:feedback_id>/', views.get_teacher_feedback, name='teacher_feedback'),
    path('teachers/', views.get_all_teachers, name='all_teachers'),
    
    # Search endpoints
    path('search/', views.search_in_videos, name='search_videos'),
]