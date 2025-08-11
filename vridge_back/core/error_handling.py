"""
Enhanced Error Handling for VideoPlanet API
Provides standardized error responses with CORS support
"""

from rest_framework.views import exception_handler
from rest_framework import status
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging
import uuid
import time

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides standardized error responses
    with proper CORS headers and logging
    """
    # Get the standard DRF response
    response = exception_handler(exc, context)
    
    # Generate request ID for tracing
    request_id = str(uuid.uuid4())[:8]
    request = context.get('request')
    
    # Add timing if available
    performance_data = {}
    if request and hasattr(request, '_start_time'):
        performance_data['response_time_ms'] = round((time.time() - request._start_time) * 1000, 2)
    
    # Custom error data structure
    custom_response_data = {
        'success': False,
        'status': 'error',
        'timestamp': time.time(),
        'request_id': request_id
    }
    
    if performance_data:
        custom_response_data['performance'] = performance_data
    
    if response is not None:
        # Handle DRF exceptions
        status_code = response.status_code
        error_code = _get_error_code_from_status(status_code)
        
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                # Validation errors
                custom_response_data['error'] = {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Validation failed',
                    'details': exc.detail,
                    'status': status_code
                }
            elif isinstance(exc.detail, list):
                # List of errors
                custom_response_data['error'] = {
                    'code': error_code,
                    'message': str(exc.detail[0]) if exc.detail else 'An error occurred',
                    'status': status_code
                }
            else:
                # Simple string error
                custom_response_data['error'] = {
                    'code': error_code,
                    'message': str(exc.detail),
                    'status': status_code
                }
        else:
            custom_response_data['error'] = {
                'code': error_code,
                'message': _get_default_error_message(status_code),
                'status': status_code
            }
        
        # Log the error
        logger.error(
            f"API Error [{request_id}]: {error_code} - {custom_response_data['error']['message']}",
            extra={
                'request_id': request_id,
                'status_code': status_code,
                'exception': str(exc),
                'path': request.path if request else None
            },
            exc_info=True
        )
        
        # Update the response data
        response.data = custom_response_data
        
    else:
        # Handle non-DRF exceptions (Django exceptions)
        status_code = 500
        error_code = 'INTERNAL_SERVER_ERROR'
        error_message = 'An internal server error occurred'
        
        # Handle specific Django exceptions
        if isinstance(exc, ValidationError):
            status_code = 400
            error_code = 'VALIDATION_ERROR'
            error_message = str(exc.message) if hasattr(exc, 'message') else str(exc)
        elif isinstance(exc, IntegrityError):
            status_code = 400
            error_code = 'INTEGRITY_ERROR'
            error_message = 'Database integrity constraint violation'
        elif isinstance(exc, PermissionError):
            status_code = 403
            error_code = 'PERMISSION_DENIED'
            error_message = 'Permission denied'
        
        custom_response_data['error'] = {
            'code': error_code,
            'message': error_message,
            'status': status_code
        }
        
        # Log the error
        logger.error(
            f"Django Exception [{request_id}]: {error_code} - {error_message}",
            extra={
                'request_id': request_id,
                'status_code': status_code,
                'exception': str(exc),
                'path': request.path if request else None
            },
            exc_info=True
        )
        
        # Create new response
        response = JsonResponse(custom_response_data, status=status_code)
    
    # Ensure CORS headers are applied
    _apply_cors_headers(response, request)
    
    return response


def _get_error_code_from_status(status_code):
    """Map HTTP status codes to error codes"""
    error_codes = {
        400: 'BAD_REQUEST',
        401: 'UNAUTHORIZED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        405: 'METHOD_NOT_ALLOWED',
        406: 'NOT_ACCEPTABLE',
        409: 'CONFLICT',
        410: 'GONE',
        412: 'PRECONDITION_FAILED',
        413: 'REQUEST_TOO_LARGE',
        415: 'UNSUPPORTED_MEDIA_TYPE',
        422: 'UNPROCESSABLE_ENTITY',
        429: 'TOO_MANY_REQUESTS',
        500: 'INTERNAL_SERVER_ERROR',
        501: 'NOT_IMPLEMENTED',
        502: 'BAD_GATEWAY',
        503: 'SERVICE_UNAVAILABLE',
        504: 'GATEWAY_TIMEOUT',
    }
    return error_codes.get(status_code, 'UNKNOWN_ERROR')


def _get_default_error_message(status_code):
    """Get default error message for status code"""
    messages = {
        400: 'Bad request - invalid data provided',
        401: 'Authentication required',
        403: 'Permission denied',
        404: 'Resource not found',
        405: 'Method not allowed',
        406: 'Not acceptable',
        409: 'Conflict - resource already exists',
        410: 'Resource no longer available',
        412: 'Precondition failed',
        413: 'Request too large',
        415: 'Unsupported media type',
        422: 'Unprocessable entity',
        429: 'Too many requests - rate limit exceeded',
        500: 'Internal server error',
        501: 'Not implemented',
        502: 'Bad gateway',
        503: 'Service unavailable',
        504: 'Gateway timeout',
    }
    return messages.get(status_code, 'An error occurred')


def _apply_cors_headers(response, request):
    """Apply CORS headers to response (backup to middleware)"""
    if not request:
        return
    
    origin = request.META.get('HTTP_ORIGIN', '')
    
    # List of allowed origins
    allowed_origins = [
        'https://vlanet.net',
        'https://www.vlanet.net',
        'https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app',
        'https://vlanet-v2-0.vercel.app',
        'http://localhost:3000',
        'http://localhost:3001',
    ]
    
    # Check origin patterns for Vercel
    import re
    origin_patterns = [
        r"^https://vlanet-v2-0-.*\.vercel\.app$",
        r"^https://.*-vlanets-projects\.vercel\.app$",
        r"^https://vlanet-.*\.vercel\.app$",
    ]
    
    is_valid_origin = origin in allowed_origins
    if not is_valid_origin:
        for pattern in origin_patterns:
            if re.match(pattern, origin):
                is_valid_origin = True
                break
    
    # Apply CORS headers for valid origins
    from django.conf import settings
    if is_valid_origin or settings.DEBUG:
        response['Access-Control-Allow-Origin'] = origin if origin else '*'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Expose-Headers'] = 'Content-Type, X-CSRFToken, Content-Length, X-Request-ID'
        
        if request.method == 'OPTIONS':
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
            response['Access-Control-Allow-Headers'] = (
                'accept, accept-encoding, authorization, content-type, dnt, origin, '
                'user-agent, x-csrftoken, x-requested-with, cache-control, pragma, '
                'x-idempotency-key'
            )
            response['Access-Control-Max-Age'] = '86400'


class APIErrorHandler:
    """Helper class for handling specific API errors"""
    
    @staticmethod
    def handle_authentication_error(request):
        """Handle authentication errors"""
        return JsonResponse({
            'success': False,
            'status': 'error',
            'error': {
                'code': 'AUTHENTICATION_FAILED',
                'message': 'Invalid authentication credentials',
                'status': 401
            },
            'timestamp': time.time(),
            'request_id': str(uuid.uuid4())[:8]
        }, status=401)
    
    @staticmethod
    def handle_rate_limit_error(request, retry_after=None):
        """Handle rate limiting errors"""
        error_data = {
            'success': False,
            'status': 'error',
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': 'Too many requests. Please try again later.',
                'status': 429
            },
            'timestamp': time.time(),
            'request_id': str(uuid.uuid4())[:8]
        }
        
        if retry_after:
            error_data['error']['retry_after'] = retry_after
        
        response = JsonResponse(error_data, status=429)
        if retry_after:
            response['Retry-After'] = str(retry_after)
        
        _apply_cors_headers(response, request)
        return response
    
    @staticmethod
    def handle_server_error(request, message="Internal server error"):
        """Handle 500 server errors"""
        error_data = {
            'success': False,
            'status': 'error',
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': message,
                'status': 500
            },
            'timestamp': time.time(),
            'request_id': str(uuid.uuid4())[:8]
        }
        
        response = JsonResponse(error_data, status=500)
        _apply_cors_headers(response, request)
        return response