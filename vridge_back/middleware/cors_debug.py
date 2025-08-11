"""CORS  """
import logging

logger = logging.getLogger(__name__)


class CorsDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #   
        origin = request.headers.get('Origin', 'No origin')
        logger.info(f"[CORS Debug] Request from origin: {origin}")
        logger.info(f"[CORS Debug] Request method: {request.method}")
        logger.info(f"[CORS Debug] Request path: {request.path}")
        
        # preflight  
        if request.method == 'OPTIONS':
            logger.info("[CORS Debug] This is a preflight request")
        
        response = self.get_response(request)
        
        #   
        logger.info(f"[CORS Debug] Response status: {response.status_code}")
        logger.info(f"[CORS Debug] Response headers: {dict(response.headers)}")
        
        # CORS  
        cors_headers = {
            'Access-Control-Allow-Origin': response.get('Access-Control-Allow-Origin', 'Not set'),
            'Access-Control-Allow-Methods': response.get('Access-Control-Allow-Methods', 'Not set'),
            'Access-Control-Allow-Headers': response.get('Access-Control-Allow-Headers', 'Not set'),
            'Access-Control-Allow-Credentials': response.get('Access-Control-Allow-Credentials', 'Not set'),
        }
        
        for header, value in cors_headers.items():
            logger.info(f"[CORS Debug] {header}: {value}")
        
        return response