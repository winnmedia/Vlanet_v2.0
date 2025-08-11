"""
API  
  API     
"""
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger('api.debug')


class APIDebugMiddleware(MiddlewareMixin):
    """API /  """
    
    def process_request(self, request):
        """  """
        if request.path.startswith('/api/') or request.path.startswith('/users/') or request.path.startswith('/projects/'):
            logger.info(f"API Request: {request.method} {request.path}")
            logger.info(f"Origin: {request.META.get('HTTP_ORIGIN', 'No origin')}")
            logger.info(f"Authorization: {'Present' if request.META.get('HTTP_AUTHORIZATION') else 'Missing'}")
            logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE', 'Not set')}")
            
            # CORS preflight  
            if request.method == 'OPTIONS':
                logger.info("CORS Preflight request detected")
    
    def process_response(self, request, response):
        """    CORS  """
        if request.path.startswith('/api/') or request.path.startswith('/users/') or request.path.startswith('/projects/'):
            logger.info(f"API Response: {response.status_code}")
            
            # CORS  
            cors_headers = {
                'Access-Control-Allow-Origin': response.get('Access-Control-Allow-Origin', 'Not set'),
                'Access-Control-Allow-Credentials': response.get('Access-Control-Allow-Credentials', 'Not set'),
                'Access-Control-Allow-Methods': response.get('Access-Control-Allow-Methods', 'Not set'),
                'Access-Control-Allow-Headers': response.get('Access-Control-Allow-Headers', 'Not set'),
            }
            logger.info(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")
            
        return response


class HealthCheckMiddleware(MiddlewareMixin):
    """  """
    
    def process_request(self, request):
        if request.path == '/api/health/':
            return JsonResponse({
                'status': 'healthy',
                'service': 'VideoplaNet Backend',
                'cors_test': {
                    'origin': request.META.get('HTTP_ORIGIN', 'No origin'),
                    'method': request.method,
                    'headers': {
                        'authorization': 'Present' if request.META.get('HTTP_AUTHORIZATION') else 'Missing',
                        'content_type': request.META.get('CONTENT_TYPE', 'Not set'),
                    }
                },
                'timestamp': str(datetime.now())
            })
        return None