"""
Railway    CORS 
  django-cors-headers   CORS .
"""
import logging
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RailwayCORSMiddleware(MiddlewareMixin):
    """
    Railway   CORS 
    django-cors-headers  CORS .
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        #  origin 
        self.allowed_origins = [
            'https://vlanet.net',
            'https://www.vlanet.net',
            'https://videoplanet-seven.vercel.app',
            'http://localhost:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:3001',
        ]
        
        #  
        self.allowed_methods = [
            'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD'
        ]
        
        #  
        self.allowed_headers = [
            'accept',
            'accept-encoding',
            'authorization',
            'content-type',
            'dnt',
            'origin',
            'user-agent',
            'x-csrftoken',
            'x-requested-with',
            'cache-control',
            'pragma',
            'x-idempotency-key',
        ]
        
        #  
        self.expose_headers = [
            'Content-Type',
            'X-CSRFToken',
            'Content-Length',
        ]
    
    def process_request(self, request):
        """OPTIONS   """
        if request.method == 'OPTIONS':
            logger.info(f"Handling OPTIONS request for {request.path}")
            response = HttpResponse()
            response['Content-Length'] = '0'
            response.status_code = 204
            return self._add_cors_headers(request, response)
        return None
    
    def process_response(self, request, response):
        """  CORS  """
        return self._add_cors_headers(request, response)
    
    def _add_cors_headers(self, request, response):
        """CORS   """
        origin = request.META.get('HTTP_ORIGIN', '')
        
        # Origin   
        if origin:
            #    origin 
            if self._is_allowed_origin(origin):
                response['Access-Control-Allow-Origin'] = origin
                response['Vary'] = 'Origin'
            else:
                #    ( )
                logger.warning(f"Allowing unregistered origin: {origin}")
                response['Access-Control-Allow-Origin'] = origin
                response['Vary'] = 'Origin'
        else:
            # Origin    (same-origin  )
            #   CORS   
            pass
        
        # Origin      
        if 'Access-Control-Allow-Origin' in response:
            # Credentials 
            response['Access-Control-Allow-Credentials'] = 'true'
            
            # OPTIONS    
            if request.method == 'OPTIONS':
                response['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
                response['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
                response['Access-Control-Max-Age'] = '86400'  # 24
            
            #    Expose Headers 
            response['Access-Control-Expose-Headers'] = ', '.join(self.expose_headers)
        
        #  
        if origin:
            logger.debug(
                f"CORS headers added - Method: {request.method}, "
                f"Path: {request.path}, Origin: {origin}, "
                f"Allow-Origin: {response.get('Access-Control-Allow-Origin', 'Not set')}"
            )
        
        return response
    
    def _is_allowed_origin(self, origin):
        """Origin    """
        #  
        if origin in self.allowed_origins:
            return True
        
        # Vercel   
        if '.vercel.app' in origin and origin.startswith('https://'):
            return True
        
        # Railway  
        if '.railway.app' in origin and origin.startswith('https://'):
            return True
        
        return False


class OptionsHandlerMiddleware(MiddlewareMixin):
    """
    OPTIONS    
         
    """
    
    def process_request(self, request):
        """OPTIONS  """
        if request.method == 'OPTIONS':
            logger.info(f"Fast OPTIONS handling for {request.path}")
            response = HttpResponse()
            response.status_code = 204
            response['Content-Length'] = '0'
            
            #  CORS  
            origin = request.META.get('HTTP_ORIGIN', '*')
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
            response['Access-Control-Allow-Headers'] = (
                'accept, accept-encoding, authorization, content-type, dnt, '
                'origin, user-agent, x-csrftoken, x-requested-with, '
                'cache-control, pragma, x-idempotency-key'
            )
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = '86400'
            response['Vary'] = 'Origin'
            
            return response
        
        return None