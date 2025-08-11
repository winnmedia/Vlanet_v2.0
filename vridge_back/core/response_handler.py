"""
VideoPlanet Enhanced API Response Handler
Provides standardized, CORS-aware, and performance-optimized API responses
"""

from django.http import JsonResponse
from rest_framework.response import Response
from .error_messages import ErrorMessages
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class StandardResponse:
    """Enhanced API Response Handler with CORS support and performance monitoring"""
    
    @staticmethod
    def _add_response_metadata(response_data, request=None):
        """Add metadata and performance info to response"""
        if request and hasattr(request, '_start_time'):
            response_data['performance'] = {
                'response_time_ms': round((time.time() - request._start_time) * 1000, 2)
            }
        
        response_data['timestamp'] = time.time()
        response_data['request_id'] = str(uuid.uuid4())[:8]
        return response_data
    
    @staticmethod
    def _create_cors_response(data, status_code=200, request=None):
        """Create JsonResponse with CORS headers already applied"""
        response = JsonResponse(data, status=status_code, safe=False)
        
        # The CORSDebugMiddleware will handle the CORS headers
        # but we can add some additional headers here for API responses
        response['Content-Type'] = 'application/json; charset=utf-8'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
    
    @staticmethod
    def success(data=None, message="Success", status_code=200, request=None):
        """Enhanced success response"""
        response_data = {
            "success": True,
            "status": "success",
            "message": message
        }
        
        if data is not None:
            response_data["data"] = data
        
        response_data = StandardResponse._add_response_metadata(response_data, request)
        return StandardResponse._create_cors_response(response_data, status_code, request)
    
    @staticmethod
    def error(error_key="SERVER_ERROR", message=None, status_code=400, details=None, request=None):
        """Enhanced error response with proper logging and CORS"""
        if message is None:
            message = getattr(ErrorMessages, error_key, ErrorMessages.SERVER_ERROR)
        
        response_data = {
            "success": False,
            "status": "error",
            "error": {
                "code": error_key,
                "message": message,
                "status": status_code
            }
        }
        
        if details:
            response_data["error"]["details"] = details
        
        # Add metadata
        response_data = StandardResponse._add_response_metadata(response_data, request)
        
        # Enhanced logging
        logger.error(f"API Error [{response_data['request_id']}]: {error_key} - {message}", extra={
            "error_code": error_key,
            "details": details,
            "status_code": status_code,
            "request_id": response_data['request_id']
        })
        
        return StandardResponse._create_cors_response(response_data, status_code, request)
    
    @staticmethod
    def paginated(data, page=1, total_pages=1, total_count=0, message=" "):
        """ """
        response = {
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
        
        if hasattr(Response, '__call__'):
            return Response(response, status=200)
        else:
            return JsonResponse(response, status=200)
    
    @staticmethod
    def created(data=None, message=" ", status_code=201):
        """  """
        return StandardResponse.success(data, message, status_code)
    
    @staticmethod
    def updated(data=None, message=" ", status_code=200):
        """  """
        return StandardResponse.success(data, message, status_code)
    
    @staticmethod
    def deleted(message=" ", status_code=200):
        """  """
        return StandardResponse.success(None, message, status_code)
    
    @staticmethod
    def not_found(resource="", message=None):
        """404 Not Found """
        if message is None:
            message = f"{resource}   ."
        return StandardResponse.error("NOT_FOUND", message, 404)
    
    @staticmethod
    def unauthorized(message=" ."):
        """401 Unauthorized """
        return StandardResponse.error("AUTH_REQUIRED", message, 401)
    
    @staticmethod
    def forbidden(message="    ."):
        """403 Forbidden """
        return StandardResponse.error("AUTH_PERMISSION_DENIED", message, 403)
    
    @staticmethod
    def validation_error(errors, message="  ."):
        """400 Validation Error """
        return StandardResponse.error("VALIDATION_FAILED", message, 400, errors)
    
    @staticmethod
    def server_error(message="  .    ."):
        """500 Internal Server Error """
        return StandardResponse.error("SERVER_ERROR", message, 500)