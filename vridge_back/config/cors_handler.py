"""
 CORS  - Railway  CORS  
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

class EmergencyCORSMiddleware(MiddlewareMixin):
    """
     CORS  - corsheaders    
    settings_base.py MIDDLEWARE    
    """
    
    def process_request(self, request):
        """OPTIONS   """
        if request.method == 'OPTIONS':
            response = HttpResponse()
            self._set_cors_headers(request, response)
            return response
        return None
    
    def process_response(self, request, response):
        """  CORS  """
        self._set_cors_headers(request, response)
        return response
    
    def _set_cors_headers(self, request, response):
        """CORS  """
        origin = request.META.get('HTTP_ORIGIN')
        
        #  origin 
        allowed_origins = [
            'https://vlanet.net',
            'https://www.vlanet.net',
            'http://localhost:3000',
            'http://localhost:3001',
        ]
        
        #    origin 
        if origin in allowed_origins or origin:  #   origin 
            response['Access-Control-Allow-Origin'] = origin
        else:
            # origin  wildcard  (    )
            response['Access-Control-Allow-Origin'] = '*'
        
        #  CORS 
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = (
            'accept, accept-encoding, authorization, content-type, dnt, '
            'origin, user-agent, x-csrftoken, x-requested-with, cache-control, pragma'
        )
        
        # OPTIONS    
        if request.method == 'OPTIONS':
            response['Access-Control-Max-Age'] = '86400'
            response['Content-Length'] = '0'
        
        #  
        logger.info(f"CORS headers set for {request.method} {request.path} from {origin}")
        
        return response