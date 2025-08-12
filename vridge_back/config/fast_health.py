"""
  
Railway    
"""
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["GET", "HEAD", "OPTIONS"])
def ultra_fast_health(request):
    """
      -   
    Railway      
    HEAD, GET, OPTIONS 메서드 지원
    """
    return HttpResponse("OK", status=200, content_type="text/plain")

def root_health(request):
    """
      
    """
    return HttpResponse("VideoPlanet Backend Running", status=200, content_type="text/plain")