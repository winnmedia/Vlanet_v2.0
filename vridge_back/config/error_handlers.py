import logging
import traceback
import os
from django.http import JsonResponse
from django.views.defaults import server_error
from django.conf import settings

logger = logging.getLogger(__name__)

def custom_500_handler(request, *args, **kwargs):
    """
     500  
              
    """
    #     
    import sys
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    if exc_type:
        #    
        logger.error(
            f"500 Error occurred:\n"
            f"Request path: {request.path}\n"
            f"Request method: {request.method}\n"
            f"User: {request.user if hasattr(request, 'user') else 'Anonymous'}\n"
            f"Exception type: {exc_type.__name__}\n"
            f"Exception value: {exc_value}\n"
            f"Traceback:\n{''.join(traceback.format_tb(exc_traceback))}"
        )
        
        #    (  )
        if request.method == 'POST':
            logger.error(f"POST data keys: {list(request.POST.keys())}")
        
        #   
        headers = {k: v for k, v in request.headers.items() 
                  if k.lower() not in ['authorization', 'cookie']}
        logger.error(f"Request headers: {headers}")
    
    # Create response based on debug mode
    if settings.DEBUG or (hasattr(settings, 'IS_RAILWAY') and settings.IS_RAILWAY and os.environ.get('ENABLE_DEBUG_TOOLBAR', 'False').lower() == 'true'):
        error_details = {
            'error': 'Internal Server Error',
            'status_code': 500,
            'path': request.path,
            'method': request.method,
        }
        
        if exc_type:
            error_details.update({
                'exception_type': exc_type.__name__,
                'exception_value': str(exc_value),
                'traceback': traceback.format_tb(exc_traceback)
            })
        
        response = JsonResponse(error_details, status=500)
    else:
        #      
        response = JsonResponse({
            'error': 'Internal Server Error',
            'message': 'An error occurred while processing your request.',
            'status_code': 500
        }, status=500)
    
    # Add CORS headers to error responses
    origin = request.META.get('HTTP_ORIGIN', '')
    if origin:
        # Check if origin is allowed
        allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        allowed_regexes = getattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES', [])
        
        is_allowed = False
        
        # Check exact match
        if origin in allowed_origins:
            is_allowed = True
        
        # Check regex patterns
        if not is_allowed and allowed_regexes:
            import re
            for pattern_str in allowed_regexes:
                if re.match(pattern_str, origin):
                    is_allowed = True
                    break
        
        # Add CORS headers if origin is allowed
        if is_allowed:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Expose-Headers'] = 'Content-Type, X-CSRFToken, X-Request-ID'
            response['Vary'] = 'Origin'
            logger.info(f"Added CORS headers to 500 error response for origin: {origin}")
    
    return response

def custom_404_handler(request, exception):
    """
     404  
    """
    logger.warning(f"404 Error - Path not found: {request.path}")
    
    response = JsonResponse({
        'error': 'Not Found',
        'message': f'The requested path {request.path} was not found.',
        'status_code': 404
    }, status=404)
    
    # Add CORS headers
    _add_cors_headers_to_response(request, response)
    return response

def custom_403_handler(request, exception):
    """
     403  
    """
    logger.warning(
        f"403 Error - Permission denied: {request.path} "
        f"for user: {request.user if hasattr(request, 'user') else 'Anonymous'}"
    )
    
    response = JsonResponse({
        'error': 'Forbidden',
        'message': 'You do not have permission to access this resource.',
        'status_code': 403
    }, status=403)
    
    # Add CORS headers
    _add_cors_headers_to_response(request, response)
    return response

def custom_400_handler(request, exception):
    """
     400  
    """
    logger.warning(f"400 Error - Bad request: {request.path}")
    
    response = JsonResponse({
        'error': 'Bad Request',
        'message': 'The request could not be understood or was missing required parameters.',
        'status_code': 400
    }, status=400)
    
    # Add CORS headers
    _add_cors_headers_to_response(request, response)
    return response


def _add_cors_headers_to_response(request, response):
    """
    Helper function to add CORS headers to error responses.
    This ensures CORS headers are present even when errors occur.
    """
    origin = request.META.get('HTTP_ORIGIN', '')
    if origin:
        # Check if origin is allowed
        allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        allowed_regexes = getattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES', [])
        
        is_allowed = False
        
        # Check exact match
        if origin in allowed_origins:
            is_allowed = True
        
        # Check regex patterns
        if not is_allowed and allowed_regexes:
            import re
            for pattern_str in allowed_regexes:
                if re.match(pattern_str, origin):
                    is_allowed = True
                    break
        
        # Add CORS headers if origin is allowed
        if is_allowed:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Expose-Headers'] = 'Content-Type, X-CSRFToken, X-Request-ID'
            response['Vary'] = 'Origin'
            logger.debug(f"Added CORS headers to error response for origin: {origin}")