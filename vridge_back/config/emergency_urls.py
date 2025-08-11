"""
 URL  -   
"""
from django.urls import path
from django.http import HttpResponse

def emergency_health(request):
    """   -  """
    return HttpResponse("OK", content_type="text/plain", status=200)

urlpatterns = [
    path("health/", emergency_health),
    path("api/health/", emergency_health),
    path("", emergency_health),  #   
]