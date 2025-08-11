import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class DebugAuthMiddleware:
    """  """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # /api/video-planning/   
        if request.path.startswith('/api/video-planning/'):
            logger.info(f"[Auth Debug] Path: {request.path}")
            logger.info(f"[Auth Debug] Method: {request.method}")
            
            #  
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            logger.info(f"[Auth Debug] Authorization Header: {auth_header}")
            
            #  
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                logger.info(f"[Auth Debug] Token: {token[:20]}...")
            
            #  
            if hasattr(request, 'user'):
                logger.info(f"[Auth Debug] User: {request.user}")
                logger.info(f"[Auth Debug] User authenticated: {request.user.is_authenticated}")
        
        response = self.get_response(request)
        return response