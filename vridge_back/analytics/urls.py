from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import views

# API endpoints
@api_view(['GET'])
def analytics_dashboard(request):
    """분석 대시보드 API"""
    return Response({
        "total_projects": 0,
        "total_users": 0,
        "total_videos": 0,
        "status": "ok"
    })

@api_view(['GET'])
def analytics_stats(request):
    """통계 API"""
    return Response({"stats": {}, "period": "last_30_days"})

urlpatterns = [
    # API patterns
    path('', analytics_dashboard, name='analytics_dashboard'),
    path('stats/', analytics_stats, name='analytics_stats'),
    
    # View patterns
    path('track/', views.TrackEventView.as_view(), name='track_event'),
    path('session/', views.SessionAnalyticsView.as_view(), name='session_analytics'),
    path('dashboard/', views.DashboardDataView.as_view(), name='dashboard_data'),
    path('realtime/', views.RealtimeMetricsView.as_view(), name='realtime_metrics'),
    path('insights/', views.UserInsightsView.as_view(), name='user_insights'),
    path('feedback/', views.FeedbackView.as_view(), name='user_feedback'),
]