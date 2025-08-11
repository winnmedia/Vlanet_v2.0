"""
  WebSocket  
"""
from django.urls import re_path
from . import websocket_consumers

websocket_urlpatterns = [
    #    
    re_path(r'ws/planning/(?P<planning_id>\d+)/collaborate/$', 
            websocket_consumers.VideoPlanningCollaborationConsumer.as_asgi()),
    
    #   WebSocket
    re_path(r'ws/notifications/$', 
            websocket_consumers.VideoPlanningNotificationConsumer.as_asgi()),
]