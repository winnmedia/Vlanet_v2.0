from .api_urls import urlpatterns as api_patterns

from django.urls import path
from . import views

urlpatterns = api_patterns + [
    #  
    path('track/', views.TrackEventView.as_view(), name='track_event'),
    path('session/', views.SessionAnalyticsView.as_view(), name='session_analytics'),
    
    #  
    path('dashboard/', views.DashboardDataView.as_view(), name='dashboard_data'),
    path('realtime/', views.RealtimeMetricsView.as_view(), name='realtime_metrics'),
    
    #   
    path('insights/', views.UserInsightsView.as_view(), name='user_insights'),
    path('feedback/', views.FeedbackView.as_view(), name='user_feedback'),
]