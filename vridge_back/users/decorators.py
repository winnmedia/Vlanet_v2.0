from functools import wraps
from django.http import JsonResponse
from .utils import user_validator
import logging

logger = logging.getLogger(__name__)

def admin_required(view_func):
    """     """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        #  user_validator  
        @user_validator
        def check_admin(request, *args, **kwargs):
            user = request.user
            
            # superuser 
            if not user.is_superuser:
                logger.warning(f"Non-admin user {user.username} attempted to access admin endpoint")
                return JsonResponse({
                    "error": "  .",
                    "code": "ADMIN_REQUIRED"
                }, status=403)
            
            #    
            return view_func(request, *args, **kwargs)
        
        return check_admin(request, *args, **kwargs)
    
    return wrapped_view