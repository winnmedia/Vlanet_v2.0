"""
   - 2025  
JWT     / 
"""

import json
import logging
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction, models
from rest_framework_simplejwt.tokens import RefreshToken
from .jwt_auth_fixed import create_tokens_for_user, debug_token
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class ImprovedSignIn(View):
    """
      
    - username/email   
    -   
    -   
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            login_id = data.get("email") or data.get("username")
            password = data.get("password")
            
            #  
            if not login_id or not password:
                return JsonResponse({
                    "success": False,
                    "message": "  .",
                    "error_code": "MISSING_CREDENTIALS"
                }, status=400)
            
            #  ( )
            logger.info(f"Login attempt for: {login_id}")
            
            #   - username email  
            user = None
            
            # 1. username 
            user = authenticate(request, username=login_id, password=password)
            
            # 2. email 
            if not user:
                email_user = User.objects.filter(email=login_id).first()
                if email_user:
                    user = authenticate(request, username=email_user.username, password=password)
            
            # 3.   
            if not user:
                #     ()
                user_exists = User.objects.filter(
                    models.Q(username=login_id) | models.Q(email=login_id)
                ).exists()
                
                if user_exists:
                    logger.warning(f"Password mismatch for user: {login_id}")
                    return JsonResponse({
                        "success": False,
                        "message": "  .",
                        "error_code": "INVALID_PASSWORD"
                    }, status=401)
                else:
                    logger.warning(f"User not found: {login_id}")
                    return JsonResponse({
                        "success": False,
                        "message": "  .",
                        "error_code": "USER_NOT_FOUND"
                    }, status=404)
            
            # 4.   
            if not user.is_active:
                return JsonResponse({
                    "success": False,
                    "message": " .  .",
                    "error_code": "ACCOUNT_DISABLED"
                }, status=403)
            
            # 5.    ()
            if hasattr(user, 'email_verified') and not user.email_verified:
                #    
                if user.date_joined.year < 2025:
                    user.email_verified = True
                    user.email_verified_at = timezone.now()
                    user.save(update_fields=['email_verified', 'email_verified_at'])
                    logger.info(f"Auto-verified legacy user: {user.username}")
            
            # 6. JWT  
            try:
                access_token, refresh_token = create_tokens_for_user(user)
                
                #    ( )
                if settings.DEBUG:
                    token_info = debug_token(access_token)
                    logger.info(f"Token created for user {user.id}: {token_info}")
                
            except Exception as e:
                logger.error(f"Token generation failed: {e}")
                return JsonResponse({
                    "success": False,
                    "message": "  .",
                    "error_code": "TOKEN_GENERATION_FAILED",
                    "detail": str(e)
                }, status=500)
            
            # 7.    
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # 8.  
            response_data = {
                "success": True,
                "message": " ",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "nickname": getattr(user, 'nickname', user.username),
                    "is_staff": user.is_staff,
                }
            }
            
            response = JsonResponse(response_data, status=200)
            
            # 9.   ()
            response.set_cookie(
                "vridge_session",
                access_token,
                max_age=60 * 60 * 24 * 7,  # 7
                httponly=True,
                secure=not settings.DEBUG,  # HTTPS secure
                samesite="Lax"
            )
            
            logger.info(f"Login successful for user: {user.username} (ID: {user.id})")
            return response
            
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": " JSON .",
                "error_code": "INVALID_JSON"
            }, status=400)
            
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return JsonResponse({
                "success": False,
                "message": "    .",
                "error_code": "INTERNAL_ERROR",
                "detail": str(e) if settings.DEBUG else None
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TokenRefreshView(View):
    """
      
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            refresh_token = data.get("refresh_token")
            
            if not refresh_token:
                return JsonResponse({
                    "success": False,
                    "message": "Refresh token .",
                    "error_code": "MISSING_REFRESH_TOKEN"
                }, status=400)
            
            #  
            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken(refresh_token)
                
                new_access_token = str(refresh.access_token)
                
                # : Refresh  
                if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                    refresh.blacklist()
                    new_refresh = RefreshToken.for_user(refresh.user)
                    new_refresh_token = str(new_refresh)
                else:
                    new_refresh_token = refresh_token
                
                return JsonResponse({
                    "success": True,
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                }, status=200)
                
            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                return JsonResponse({
                    "success": False,
                    "message": "  .",
                    "error_code": "TOKEN_REFRESH_FAILED",
                    "detail": str(e)
                }, status=401)
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}", exc_info=True)
            return JsonResponse({
                "success": False,
                "message": "    .",
                "error_code": "INTERNAL_ERROR"
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TokenVerifyView(View):
    """
      
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            token = data.get("token")
            
            if not token:
                return JsonResponse({
                    "success": False,
                    "message": "  .",
                    "error_code": "MISSING_TOKEN"
                }, status=400)
            
            #  
            from rest_framework_simplejwt.tokens import AccessToken
            try:
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                
                #  
                user = User.objects.filter(id=user_id, is_active=True).first()
                if not user:
                    raise Exception("User not found or inactive")
                
                return JsonResponse({
                    "success": True,
                    "valid": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                }, status=200)
                
            except Exception as e:
                logger.debug(f"Token verification failed: {e}")
                return JsonResponse({
                    "success": False,
                    "valid": False,
                    "message": "  .",
                    "error_code": "INVALID_TOKEN"
                }, status=401)
                
        except Exception as e:
            logger.error(f"Token verify error: {e}", exc_info=True)
            return JsonResponse({
                "success": False,
                "message": "    .",
                "error_code": "INTERNAL_ERROR"
            }, status=500)