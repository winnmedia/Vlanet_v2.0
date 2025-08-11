"""
  
Railway    
"""
from django.http import HttpResponse

def ultra_fast_health(request):
    """
      -   
    Railway      
    """
    return HttpResponse("OK", status=200, content_type="text/plain")

def root_health(request):
    """
      
    """
    return HttpResponse("VideoPlanet Backend Running", status=200, content_type="text/plain")