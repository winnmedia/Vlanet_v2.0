"""
  Fallback 
Railway     
"""
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def _is_railway_env():
    """Railway  """
    return (
        os.environ.get('RAILWAY_ENVIRONMENT') is not None or
        os.environ.get('RAILWAY_PROJECT_ID') is not None or
        'railway' in os.environ.get('DJANGO_SETTINGS_MODULE', '')
    )

def get_auth_views():
    """     """
    
    #    
    try:
        from users.views_signup_safe import SafeSignUp, SafeSignIn
        from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
        
        safe_views = {
            'login': SafeSignIn,
            'signup': SafeSignUp,
            'refresh': TokenRefreshView,
            'verify': TokenVerifyView
        }
        logger.info("Safe auth views loaded successfully")
    except ImportError as e:
        logger.error(f"Failed to import safe views: {e}")
        #  
        from django.views import View
        from django.http import JsonResponse
        
        class FallbackView(View):
            def post(self, request):
                return JsonResponse({
                    "error": "Authentication system temporarily unavailable",
                    "message": "Please try again later"
                }, status=503)
        
        safe_views = {
            'login': FallbackView,
            'signup': FallbackView,
            'refresh': FallbackView,
            'verify': FallbackView
        }
    
    # Railway    
    if _is_railway_env():
        logger.info("Railway environment detected - using safe views")
        return safe_views
    
    # /    
    try:
        from users.views_auth_fixed import ImprovedSignIn
        from users.views_auth_improved import ImprovedSignUp
        
        improved_views = {
            'login': ImprovedSignIn,
            'signup': ImprovedSignUp,
            'refresh': TokenRefreshView,
            'verify': TokenVerifyView
        }
        logger.info("Improved auth views loaded successfully")
        return improved_views
    except ImportError:
        logger.info("Improved views not available, using safe views")
        return safe_views
    
    return safe_views