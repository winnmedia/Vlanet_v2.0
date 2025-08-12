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
    
    # Railway    
    if _is_railway_env():
        logger.info("Railway environment detected - using Railway-optimized views")
        try:
            from users.railway_auth import RailwayLogin, RailwaySignup
            from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
            
            railway_views = {
                'login': RailwayLogin,
                'signup': RailwaySignup,
                'refresh': TokenRefreshView,
                'verify': TokenVerifyView
            }
            logger.info("Railway: Optimized auth views loaded successfully")
            return railway_views
        except ImportError as e:
            logger.error(f"Railway: Failed to import Railway views: {e}, trying safe views")
            # Safe views fallback
            try:
                from users.views_signup_safe import SafeSignUp, SafeSignIn
                from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
                
                safe_views = {
                    'login': SafeSignIn,
                    'signup': SafeSignUp,
                    'refresh': TokenRefreshView,
                    'verify': TokenVerifyView
                }
                logger.info("Railway: Safe auth views loaded as fallback")
                return safe_views
            except ImportError as e2:
                logger.error(f"Railway: Failed to import any auth views: {e2}")
                #  
                from django.views import View
                from django.http import JsonResponse
                
                class FallbackView(View):
                    def post(self, request):
                        return JsonResponse({
                            "error": "Authentication system temporarily unavailable",
                            "message": "Please try again later"
                        }, status=503)
                
                return {
                    'login': FallbackView,
                    'signup': FallbackView,
                    'refresh': FallbackView,
                    'verify': FallbackView
                }
    
    # /    
    try:
        from users.views_auth_fixed import ImprovedSignIn
        from users.views_auth_improved import ImprovedSignUp
        from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
        
        improved_views = {
            'login': ImprovedSignIn,
            'signup': ImprovedSignUp,
            'refresh': TokenRefreshView,
            'verify': TokenVerifyView
        }
        logger.info("Development: Improved auth views loaded successfully")
        return improved_views
    except ImportError as e:
        logger.info(f"Development: Improved views not available ({e}), using safe views")
        # Safe views   
        try:
            from users.views_signup_safe import SafeSignUp, SafeSignIn
            from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
            
            safe_views = {
                'login': SafeSignIn,
                'signup': SafeSignUp,
                'refresh': TokenRefreshView,
                'verify': TokenVerifyView
            }
            logger.info("Development: Safe auth views loaded as fallback")
            return safe_views
        except ImportError as e2:
            logger.error(f"Development: Failed to import any auth views: {e2}")
            #  
            from django.views import View
            from django.http import JsonResponse
            
            class FallbackView(View):
                def post(self, request):
                    return JsonResponse({
                        "error": "Authentication system temporarily unavailable",
                        "message": "Please try again later"
                    }, status=503)
            
            return {
                'login': FallbackView,
                'signup': FallbackView,
                'refresh': FallbackView,
                'verify': FallbackView
            }