"""
CORS    
"""
import os
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class CORSDebugView(View):
    """CORS   """
    
    def get(self, request):
        """ CORS  """
        cors_settings = {
            "CORS_ALLOW_ALL_ORIGINS": getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', None),
            "CORS_ALLOWED_ORIGINS": getattr(settings, 'CORS_ALLOWED_ORIGINS', None),
            "CORS_ALLOW_CREDENTIALS": getattr(settings, 'CORS_ALLOW_CREDENTIALS', None),
            "CORS_ALLOW_HEADERS": getattr(settings, 'CORS_ALLOW_HEADERS', None),
            "CORS_ALLOW_METHODS": getattr(settings, 'CORS_ALLOW_METHODS', None),
            "CORS_PREFLIGHT_MAX_AGE": getattr(settings, 'CORS_PREFLIGHT_MAX_AGE', None),
            "MIDDLEWARE": [m for m in settings.MIDDLEWARE if 'cors' in m.lower()],
            "REQUEST_ORIGIN": request.META.get('HTTP_ORIGIN', 'No origin header'),
            "REQUEST_METHOD": request.method,
            "DJANGO_SETTINGS_MODULE": os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set'),
            "RAILWAY_ENVIRONMENT": os.environ.get('RAILWAY_ENVIRONMENT', 'Not in Railway'),
        }
        
        logger.info(f"CORS Debug Info: {cors_settings}")
        
        response = JsonResponse({
            "status": "ok",
            "cors_settings": cors_settings,
            "message": "CORS configuration debug info"
        })
        
        #   CORS   
        origin = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = 'accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        
        return response
    
    def options(self, request):
        """OPTIONS  """
        response = JsonResponse({
            "status": "ok",
            "message": "CORS preflight check"
        })
        
        origin = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = 'accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Max-Age'] = '86400'
        
        return response