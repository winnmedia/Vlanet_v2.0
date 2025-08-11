"""
VideoPlanet   
 API    
"""

from django.http import JsonResponse
from rest_framework.response import Response
from .error_messages import ErrorMessages
import logging

logger = logging.getLogger(__name__)


class StandardResponse:
    """ API """
    
    @staticmethod
    def success(data=None, message="", status_code=200):
        """ """
        response = {
            "success": True,
            "message": message
        }
        
        if data is not None:
            response["data"] = data
        
        #  JsonResponse  (Django View )
        return JsonResponse(response, status=status_code)
    
    @staticmethod
    def error(error_key="SERVER_ERROR", message=None, status_code=400, details=None):
        """ """
        if message is None:
            message = getattr(ErrorMessages, error_key, ErrorMessages.SERVER_ERROR)
        
        response = {
            "success": False,
            "error": {
                "code": error_key,
                "message": message
            }
        }
        
        if details:
            response["error"]["details"] = details
        
        #  
        logger.error(f"API Error: {error_key} - {message}", extra={
            "error_code": error_key,
            "details": details,
            "status_code": status_code
        })
        
        #  JsonResponse  (Django View )
        return JsonResponse(response, status=status_code)
    
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