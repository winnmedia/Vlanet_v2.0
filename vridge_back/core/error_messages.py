#    
"""
VideoPlanet   
      
"""

class ErrorMessages:
    """  """
    
    #  
    AUTH_REQUIRED = " ."
    AUTH_INVALID_CREDENTIALS = "    ."
    AUTH_TOKEN_EXPIRED = "  .  ."
    AUTH_TOKEN_INVALID = "   ."
    AUTH_PERMISSION_DENIED = "    ."
    
    #  
    USER_NOT_FOUND = "   ."
    USER_ALREADY_EXISTS = "  ."
    USER_PROFILE_UPDATE_FAILED = "  ."
    
    #  
    PROJECT_NOT_FOUND = "   ."
    PROJECT_ALREADY_EXISTS = "    ."
    PROJECT_CREATE_FAILED = "  ."
    PROJECT_UPDATE_FAILED = "  ."
    PROJECT_DELETE_FAILED = "  ."
    PROJECT_ACCESS_DENIED = "    ."
    
    #  
    FEEDBACK_NOT_FOUND = "   ."
    FEEDBACK_CREATE_FAILED = "  ."
    FEEDBACK_UPDATE_FAILED = "  ."
    FEEDBACK_DELETE_FAILED = "  ."
    FEEDBACK_ACCESS_DENIED = "    ."
    FEEDBACK_VIDEO_UPLOAD_FAILED = "  ."
    FEEDBACK_ENCODING_FAILED = "  ."
    
    #  
    FILE_NOT_FOUND = "   ."
    FILE_UPLOAD_FAILED = "  ."
    FILE_SIZE_EXCEEDED = "   . ( 500MB)"
    FILE_TYPE_NOT_ALLOWED = "   ."
    
    #  
    VALIDATION_FAILED = "  ."
    REQUIRED_FIELD_MISSING = "  ."
    INVALID_FORMAT = "  ."
    INVALID_DATE_RANGE = "   ."
    
    #  
    SERVER_ERROR = "  .    ."
    DATABASE_ERROR = "  ."
    EXTERNAL_API_ERROR = "   ."
    
    @classmethod
    def get_error_response(cls, error_key, status_code=400, details=None):
        """   """
        error_message = getattr(cls, error_key, cls.SERVER_ERROR)
        
        response = {
            "success": False,
            "error": {
                "code": error_key,
                "message": error_message
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        return response, status_code