"""
Enhanced CORS Middleware that guarantees headers on all responses
"""
import logging
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
import re

logger = logging.getLogger('corsheaders')


class GuaranteedCORSMiddleware(MiddlewareMixin):
    """
    Middleware that absolutely guarantees CORS headers are present on every response,
    including error responses, exceptions, and Django's built-in error pages.
    This should be placed AFTER django-cors-headers in the middleware stack.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        
        # Compile regex patterns once for performance
        self.origin_regex_patterns = [
            re.compile(pattern) for pattern in getattr(
                settings, 
                'CORS_ALLOWED_ORIGIN_REGEXES', 
                []
            )
        ]
        
        self.allowed_origins = set(getattr(
            settings, 
            'CORS_ALLOWED_ORIGINS', 
            []
        ))
    
    def is_origin_allowed(self, origin):
        """Check if the origin is allowed based on settings"""
        if not origin:
            return False
            
        # Check exact match
        if origin in self.allowed_origins:
            return True
            
        # Check regex patterns
        for pattern in self.origin_regex_patterns:
            if pattern.match(origin):
                return True
                
        # In DEBUG mode, also allow localhost origins
        if settings.DEBUG:
            if origin.startswith('http://localhost:') or origin.startswith('http://127.0.0.1:'):
                return True
                
        return False
    
    def add_cors_headers(self, request, response):
        """Add CORS headers to the response"""
        origin = request.META.get('HTTP_ORIGIN', '')
        
        # Generate request ID for tracking
        if not hasattr(request, 'id'):
            request.id = str(uuid.uuid4())[:8]
        
        # Check if headers are already set by django-cors-headers
        if 'Access-Control-Allow-Origin' in response:
            logger.debug(f"[{request.id}] CORS headers already present")
            return response
        
        # Determine if origin is allowed
        if self.is_origin_allowed(origin):
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            logger.info(f"[{request.id}] CORS headers added for origin: {origin}")
        elif settings.DEBUG:
            # In debug mode, be more permissive
            response['Access-Control-Allow-Origin'] = origin if origin else '*'
            response['Access-Control-Allow-Credentials'] = 'true' if origin else 'false'
            logger.debug(f"[{request.id}] DEBUG: CORS headers added for origin: {origin or '*'}")
        else:
            # In production, log the rejected origin
            logger.warning(f"[{request.id}] CORS: Rejected origin: {origin}")
            # Still set headers for error visibility
            response['Access-Control-Allow-Origin'] = 'null'
            response['Access-Control-Allow-Credentials'] = 'false'
        
        # Always add these headers
        response['Access-Control-Expose-Headers'] = 'Content-Type, X-CSRFToken, X-Request-ID'
        response['X-Request-ID'] = request.id
        
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
            response['Access-Control-Allow-Headers'] = (
                'accept, accept-encoding, authorization, content-type, dnt, origin, '
                'user-agent, x-csrftoken, x-requested-with, cache-control, pragma, '
                'x-idempotency-key, x-request-id'
            )
            response['Access-Control-Max-Age'] = '86400'
            response.status_code = 200
            response.content = b''
        
        return response
    
    def process_response(self, request, response):
        """Process all responses to ensure CORS headers"""
        return self.add_cors_headers(request, response)
    
    def process_exception(self, request, exception):
        """Handle exceptions and ensure CORS headers on error responses"""
        logger.error(f"Exception occurred: {exception}", exc_info=True)
        
        # Create error response
        response = JsonResponse({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'request_id': getattr(request, 'id', 'unknown')
        }, status=500)
        
        # Add CORS headers to error response
        return self.add_cors_headers(request, response)


def rest_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework that ensures CORS headers
    """
    from rest_framework.views import exception_handler
    
    # Get the standard error response
    response = exception_handler(exc, context)
    
    if response is not None:
        # Add request ID to response
        request = context.get('request')
        if request and hasattr(request, 'id'):
            response['X-Request-ID'] = request.id
        
        # Ensure CORS headers are present
        if request:
            origin = request.META.get('HTTP_ORIGIN', '')
            if origin and 'Access-Control-Allow-Origin' not in response:
                # Let the middleware handle it, but set a flag
                response._cors_needed = True
        
        # Add error details to response data
        if hasattr(response, 'data'):
            if not isinstance(response.data, dict):
                response.data = {'detail': response.data}
            response.data['status_code'] = response.status_code
            if request and hasattr(request, 'id'):
                response.data['request_id'] = request.id
    
    return response