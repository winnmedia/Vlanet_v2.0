# -*- coding: utf-8 -*-
"""
   -    
"""
import logging
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings
from . import models
from .validators import InputValidator

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SafeSignUp(View):
    """     """
    
    def post(self, request):
        try:
            # request.body 
            if not request.body:
                return JsonResponse({"message": "  ."}, status=400)
            
            try:
                data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"JSON  : {str(e)}")
                return JsonResponse({"message": " JSON ."}, status=400)
            
            email = data.get("email")
            nickname = data.get("nickname")
            password = data.get("password")

            #  
            if not email or not nickname or not password:
                return JsonResponse({"message": "  ."}, status=400)
            
            #   
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return JsonResponse({
                    "success": False,
                    "message": error_msg,
                    "field": "email"
                }, status=400)
            
            #  
            is_valid, error_msg = InputValidator.validate_text_input(nickname, "", max_length=50)
            if not is_valid:
                return JsonResponse({
                    "success": False,
                    "message": error_msg,
                    "field": "nickname"
                }, status=400)
            
            if len(nickname) < 2:
                return JsonResponse({"message": "  2  ."}, status=400)
            
            #  
            is_valid, error_msg = InputValidator.validate_password(password)
            if not is_valid:
                return JsonResponse({
                    "success": False,
                    "message": error_msg,
                    "field": "password"
                }, status=400)

            logger.info(f"  - : {email}, : {nickname}")
            
            #   
            user = models.User.objects.filter(username=email).first()
            if user:
                return JsonResponse({"message": "   ."}, status=409)
            
            #   
            nickname_exists = models.User.objects.filter(nickname=nickname).exists()
            if nickname_exists:
                return JsonResponse({"message": "   ."}, status=409)
            
            #   
            new_user = models.User(
                username=email, 
                email=email,
                nickname=nickname,
                login_method='email'
            )
            new_user.set_password(password)
            
            # Railway      
            if settings.DEBUG or 'railway' in request.get_host().lower():
                new_user.email_verified = True
                new_user.email_verified_at = timezone.now()
                logger.info(f"   : {email}")
            
            new_user.save()
            
            logger.info(f"  - ID: {new_user.id}, : {new_user.username}")

            #   
            return JsonResponse({
                "message": " .   .",
                "email_sent": False,
                "user": new_user.username,
                "nickname": new_user.nickname,
                "auto_verified": new_user.email_verified
            }, status=201)
            
        except Exception as e:
            logger.error(f" : {str(e)}", exc_info=True)
            return JsonResponse({"message": f"    : {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SafeSignIn(View):
    """  """
    
    def post(self, request):
        try:
            # request.body 
            if not request.body:
                return JsonResponse({"message": "  ."}, status=400)
            
            try:
                data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"JSON  : {str(e)}")
                return JsonResponse({"message": " JSON ."}, status=400)
            
            # username  email      
            email = data.get("email") or data.get("username")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"message": "  ."}, status=400)

            logger.info(f"  - email: {email}")
            
            #  
            from django.contrib.auth import authenticate
            
            #  username 
            user = authenticate(request, username=email, password=password)
            
            if not user:
                # email  
                user_obj = models.User.objects.filter(email=email).first()
                if user_obj:
                    logger.info(f"Found user by email: {user_obj.username}")
                    # username  authenticate
                    user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                #    (/  )
                if hasattr(user, 'email_verified') and not user.email_verified:
                    if settings.DEBUG or 'railway' in request.get_host().lower():
                        logger.info(f"  : {user.email}")
                        user.email_verified = True
                        user.email_verified_at = timezone.now()
                        user.save()
                
                # JWT  
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                
                res = JsonResponse({
                    "message": "success",
                    "access": access_token,
                    "refresh": refresh_token,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "vridge_session": access_token,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "nickname": user.nickname if user.nickname else user.username,
                    }
                }, status=200)
                
                res.set_cookie(
                    "vridge_session",
                    access_token,
                    httponly=True,
                    samesite="Lax",
                    secure=True,
                    max_age=2419200,
                )
                return res
            else:
                logger.error(f" : {email}")
                return JsonResponse({"message": "    ."}, status=401)
                
        except Exception as e:
            logger.error(f" : {str(e)}", exc_info=True)
            return JsonResponse({"message": f"    : {str(e)}"}, status=500)