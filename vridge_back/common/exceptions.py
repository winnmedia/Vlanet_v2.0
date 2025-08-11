from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class APIException:
    """ API   """
    
    @staticmethod
    def bad_request(message=" .", details=None):
        """400 Bad Request -   """
        response_data = {"error": message}
        if details:
            response_data["details"] = details
        return JsonResponse(response_data, status=400)
    
    @staticmethod
    def unauthorized(message=" .", details=None):
        """401 Unauthorized -  """
        response_data = {"error": message}
        if details:
            response_data["details"] = details
        return JsonResponse(response_data, status=401)
    
    @staticmethod
    def forbidden(message=" .", details=None):
        """403 Forbidden -  """
        response_data = {"error": message}
        if details:
            response_data["details"] = details
        return JsonResponse(response_data, status=403)
    
    @staticmethod
    def not_found(message="   .", details=None):
        """404 Not Found -  """
        response_data = {"error": message}
        if details:
            response_data["details"] = details
        return JsonResponse(response_data, status=404)
    
    @staticmethod
    def conflict(message="  .", details=None):
        """409 Conflict -  """
        response_data = {"error": message}
        if details:
            response_data["details"] = details
        return JsonResponse(response_data, status=409)
    
    @staticmethod
    def too_many_requests(message="  .    .", details=None):
        """429 Too Many Requests - Rate Limit """
        response_data = {"error": message}
        if details:
            response_data["details"] = details
        return JsonResponse(response_data, status=429)
    
    @staticmethod
    def internal_server_error(message="  .", details=None):
        """500 Internal Server Error -  """
        response_data = {"error": message}
        if details:
            response_data["details"] = details
        logger.error(f"Internal Server Error: {message} - {details}")
        return JsonResponse(response_data, status=500)
    
    @staticmethod
    def success(message="success", data=None):
        """200 OK -  """
        response_data = {"message": message}
        if data:
            response_data.update(data)
        return JsonResponse(response_data, status=200)
    
    @staticmethod
    def created(message=".", data=None):
        """201 Created -   """
        response_data = {"message": message}
        if data:
            response_data.update(data)
        return JsonResponse(response_data, status=201)