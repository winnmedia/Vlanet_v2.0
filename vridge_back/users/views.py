# -*- coding: utf-8 -*-
import logging, json, random, requests
import os

logger = logging.getLogger(__name__)
from django.conf import settings
from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth import authenticate
from . import models
from django.views import View
from django.http import JsonResponse
from .utils import user_validator, auth_send_email
from core.security import sanitize_input, set_secure_cookie, rate_limit, SecurityError
from .security_utils import PasswordResetSecurity
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from .validators import InputValidator, validate_request_data
from core.response_handler import StandardResponse
from core.error_messages import ErrorMessages

# from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView


########## username kakao,naver,google    x
#   
@method_decorator(csrf_exempt, name='dispatch')
class CheckEmail(View):
    def post(self, request):
        try:
            # request.body 
            if not request.body:
                return JsonResponse({"message": "  ."}, status=400)
            
            try:
                data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"JSON parsing error in CheckEmail: {str(e)}")
                return JsonResponse({"message": " JSON ."}, status=400)
            
            email = data.get("email")
            
            #   
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return StandardResponse.validation_error({"email": error_msg})
            
            # Database query with connection error handling
            try:
                # N+1  :   
                # username  email  
                user = models.User.objects.filter(email=email).first()
                if user:
                    # 409  200  ( )
                    return JsonResponse({
                        "success": False,
                        "available": False,
                        "message": "   .",
                        "code": "USER_ALREADY_EXISTS"
                    }, status=200)
                else:
                    return JsonResponse({
                        "success": True,
                        "available": True,
                        "message": "  ."
                    }, status=200)
            except Exception as db_error:
                logger.error(f"Database error in CheckEmail for email {email}: {str(db_error)}", exc_info=True)
                # Return a safe error response that indicates temporary issue
                return JsonResponse({
                    "message": "    .   .",
                    "error_code": "DB_CONNECTION_ERROR"
                }, status=503)  # Service Unavailable
                
        except Exception as e:
            logger.error(f"Unexpected error in CheckEmail: {str(e)}", exc_info=True)
            return StandardResponse.server_error()


#   
@method_decorator(csrf_exempt, name='dispatch')
class CheckNickname(View):
    def post(self, request):
        try:
            # request.body 
            if not request.body:
                return JsonResponse({"message": "  ."}, status=400)
            
            try:
                data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"JSON parsing error in CheckNickname: {str(e)}")
                return JsonResponse({"message": " JSON ."}, status=400)
            
            nickname = data.get("nickname")
            
            if not nickname:
                return JsonResponse({"message": " ."}, status=400)
            
            if len(nickname) < 2:
                return JsonResponse({"message": "  2  ."}, status=400)
            
            # Database query with connection error handling
            try:
                # N+1  :   
                user = models.User.objects.filter(nickname=nickname).first()
                if user:
                    return JsonResponse({"message": "   ."}, status=409)
                else:
                    return JsonResponse({"message": "  ."}, status=200)
            except Exception as db_error:
                logger.error(f"Database error in CheckNickname for nickname {nickname}: {str(db_error)}", exc_info=True)
                # Return a safe error response that indicates temporary issue
                return JsonResponse({
                    "message": "    .   .",
                    "error_code": "DB_CONNECTION_ERROR"
                }, status=503)  # Service Unavailable
                
        except Exception as e:
            logger.error(f"Unexpected error in CheckNickname: {str(e)}", exc_info=True)
            return StandardResponse.server_error()


@method_decorator(csrf_exempt, name='dispatch')
class SignUp(View):
    def post(self, request):
        try:
            # request.body 
            if not request.body:
                return JsonResponse({"message": "  ."}, status=400)
            
            try:
                data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"JSON  : {str(e)}, Body: {request.body[:100]}")
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
            user = models.User.objects.get_or_none(username=email)
            if user:
                return JsonResponse({"message": "   ."}, status=409)
            
            #   
            nickname_exists = models.User.objects.filter(nickname=nickname).exists()
            if nickname_exists:
                return JsonResponse({"message": "   ."}, status=409)
            
            #   
            new_user = models.User(
                username=email, 
                email=email,  # email  
                nickname=nickname,
                login_method='email'
            )
            #        
            if hasattr(new_user, 'is_social_login'):
                new_user.is_social_login = False
            if hasattr(new_user, 'social_id'):
                new_user.social_id = None
            if hasattr(new_user, 'social_profile_image'):
                new_user.social_profile_image = None
            if hasattr(new_user, 'login_count'):
                new_user.login_count = 0
            if hasattr(new_user, 'last_login_ip'):
                new_user.last_login_ip = None
            new_user.set_password(password)
            new_user.save()
            
            #  DevelopmentFramework  (   )
            try:
                self._create_default_framework(new_user)
                logger.info(f"    - : {new_user.username}")
            except Exception as framework_error:
                logger.warning(f"    (  ): {str(framework_error)}")
                #      
            
            logger.info(f"  - ID: {new_user.id}, : {new_user.username}")

            #    (  )
            email_sent = False
            try:
                from .email_verification_service import EmailVerificationService
                verification_token = EmailVerificationService.send_verification_email(new_user)
                if verification_token:
                    email_sent = True
                    logger.info(f"    - : {new_user.username}")
                else:
                    logger.warning(f"    - : {new_user.username}")
            except Exception as email_error:
                logger.error(f"  : {str(email_error)}")
                #        
                if settings.DEBUG or 'railway' in request.get_host().lower():
                    new_user.email_verified = True
                    new_user.email_verified_at = timezone.now()
                    new_user.save()
                    logger.info(f"  -    : {new_user.username}")
            
            #   
            if email_sent:
                return JsonResponse({
                    "message": " .    .",
                    "email_sent": True,
                    "user": new_user.username,
                    "nickname": new_user.nickname,
                }, status=201)
            else:
                #     
                return JsonResponse({
                    "message": " .   .",
                    "email_sent": False,
                    "user": new_user.username,
                    "nickname": new_user.nickname,
                    "auto_verified": new_user.email_verified
                }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"message": "  ."}, status=400)
        except Exception as e:
            logger.error(f" : {str(e)}", exc_info=True)
            logging.error(f"SignUp Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"message": "    ."}, status=500)
    
    def _create_default_framework(self, user):
        """  DevelopmentFramework """
        try:
            from projects.models import DevelopmentFramework
            
            #     
            if DevelopmentFramework.objects.filter(user=user, is_default=True).exists():
                return
            
            #   
            default_framework = DevelopmentFramework.objects.create(
                user=user,
                name="  ",
                intro_hook=" 5       .  ,   ,       .",
                immersion="       .    ,        .",
                twist="        .          .",
                hook_next="      . ' ...', ' ...'        .",
                is_default=True
            )
            logger.info(f"   : {user.username}")
            
        except ImportError:
            logger.warning("DevelopmentFramework     -     ")
        except Exception as e:
            logger.error(f"    : {str(e)}")
            #      
            pass


@method_decorator(csrf_exempt, name='dispatch')
class SignIn(View):
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

            # Debug
            logger.info(f"Login attempt - email: {email}")
            
            # Django authenticate 
            user = None
            
            #  username 
            user = authenticate(request, username=email, password=password)
            
            if not user:
                # email  
                user_obj = models.User.objects.filter(email=email).first()
                if user_obj:
                    logger.info(f"Found user by email: {user_obj.username}")
                    # username  authenticate
                    user = authenticate(request, username=user_obj.username, password=password)
            
            if not user:
                logger.error(f"Authentication failed for: {email}")
                #    
                test_user = models.User.objects.filter(username=email).first()
                if not test_user:
                    test_user = models.User.objects.filter(email=email).first()
                    
                if test_user:
                    logger.error(f"User exists but auth failed: username={test_user.username}, active={test_user.is_active}")
                else:
                    logger.error(f"User not found: {email}")
            
            if user is not None:
                #    -     
                if hasattr(user, 'email_verified') and not user.email_verified:
                    #        
                    if settings.DEBUG or not hasattr(user, 'email_verified_at') or user.email_verified_at is None:
                        logger.info(f"    : {user.email}")
                        user.email_verified = True
                        user.email_verified_at = timezone.now()
                        user.save()
                    else:
                        return JsonResponse(
                            {
                                "message": "  .     .",
                                "error_code": "EMAIL_NOT_VERIFIED",
                                "email": user.email
                            },
                            status=403
                        )
                
                #    
                if not user.is_active:
                    logger.warning(f"   : {user.email}")
                    return JsonResponse({
                        "message": " .  ."
                    }, status=403)
                
                # JWT      
                try:
                    from rest_framework_simplejwt.tokens import RefreshToken
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)
                    
                    #     
                    logger.info(f"  - : {user.username}, ID: {user.id}")
                    
                    #     ( )
                    user_data = {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email if user.email else user.username,
                        "nickname": user.nickname if user.nickname else user.username,
                        "login_method": getattr(user, 'login_method', 'email'),
                        "email_verified": getattr(user, 'email_verified', True)
                    }
                    
                    response_data = {
                        "message": "success",
                        "status": "success",
                        "access": access_token,  #  JWT 
                        "refresh": refresh_token,  #  JWT 
                        "access_token": access_token,  #   
                        "refresh_token": refresh_token,
                        "vridge_session": access_token,  #  
                        "user": user_data
                    }
                    
                    res = JsonResponse(response_data, status=200)
                    
                    # HttpOnly   ( )
                    secure_cookie = not settings.DEBUG  # HTTPS  Secure 
                    res.set_cookie(
                        "vridge_session",
                        access_token,
                        httponly=True,
                        samesite="Lax",
                        secure=secure_cookie,
                        max_age=3600,  # 1 (  )
                    )
                    
                    return res
                    
                except Exception as token_error:
                    logger.error(f"JWT   : {str(token_error)}")
                    return JsonResponse({
                        "message": "    ."
                    }, status=500)
            else:
                logger.warning(f"  - : {email}")
                return JsonResponse({
                    "message": "    .",
                    "status": "error",
                    "error_code": "INVALID_CREDENTIALS"
                }, status=401)
        except Exception as e:
            logger.error(f"Error in CheckEmail: {str(e)}", exc_info=True)
            return JsonResponse({"message": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SendAuthNumber(View):
    def post(self, request, types):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            
            #   
            import re
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not email or not re.match(email_regex, email):
                return JsonResponse({"message": "   ."}, status=400)

            # Rate limiting 
            client_ip = request.META.get('REMOTE_ADDR', '')
            rate_ok, rate_msg = PasswordResetSecurity.check_rate_limit(
                f"{client_ip}:{email}", 
                "auth_request", 
                limit=3, 
                window=300  # 5
            )
            if not rate_ok:
                return JsonResponse({"message": rate_msg}, status=429)

            #     
            auth_number = PasswordResetSecurity.generate_auth_code()

            user = models.User.objects.get_or_none(username=email)

            if types == "reset":
                if user is None:
                    return JsonResponse({"message": "  ."}, status=404)

                if user.login_method != "email":
                    return JsonResponse({"message": "  ."}, status=400)

                #     (10 )
                PasswordResetSecurity.store_auth_code(email, auth_number, expiry_minutes=10)
            else:
                if user:
                    return JsonResponse({"message": "   ."}, status=409)
                email_verify, is_created = models.EmailVerify.objects.get_or_create(email=email)
                email_verify.auth_number = auth_number
                email_verify.save()

            try:
                result = auth_send_email(request, email, auth_number)
                if result:
                    logging.info(f"Auth email sent successfully to {email}")
                    return JsonResponse({
                        "message": "success",
                        "detail": "  . 10  .",
                        "email": email
                    }, status=200)
                else:
                    logging.error(f"Email sending failed for {email}")
                    return JsonResponse({
                        "message": "  .    ."
                    }, status=500)
            except Exception as email_error:
                logging.error(f"Email sending error: {str(email_error)}")
                return JsonResponse({
                    "message": "    ."
                }, status=500)
        except Exception as e:
            logging.error(str(e))
            return JsonResponse({"message": "     ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EmailAuth(View):
    def post(self, request, types):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            auth_number = data.get("auth_number")

            if not email or not auth_number:
                return JsonResponse({"message": "  ."}, status=400)

            # Rate limiting  ( )
            client_ip = request.META.get('REMOTE_ADDR', '')
            rate_ok, rate_msg = PasswordResetSecurity.check_rate_limit(
                f"{client_ip}:{email}", 
                "auth_verify", 
                limit=5, 
                window=300  # 5
            )
            if not rate_ok:
                return JsonResponse({"message": rate_msg}, status=429)

            if types == "reset":
                user = models.User.objects.get_or_none(username=email)

                if not user:
                    return JsonResponse({"message": "  ."}, status=404)

                #    
                is_valid, error_msg = PasswordResetSecurity.verify_and_get_auth_code(
                    email, str(auth_number)
                )
                
                if is_valid:
                    #   
                    reset_token = PasswordResetSecurity.generate_reset_token(user.id)
                    return JsonResponse({
                        "message": "success",
                        "reset_token": reset_token
                    }, status=200)
                else:
                    return StandardResponse.validation_error({"email": error_msg})

            else:
                email_verify = models.EmailVerify.objects.get_or_none(email=email)
                if not email_verify:
                    return JsonResponse({"message": "    ."}, status=404)
                if str(email_verify.auth_number) == str(auth_number):
                    email_verify.delete()
                    return JsonResponse({"message": "success"}, status=200)
                else:
                    return JsonResponse({"message": "  "}, status=400)

        except Exception as e:
            logging.error(str(e))
            return JsonResponse({"message": "     ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ResetPassword(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
            reset_token = data.get("reset_token")

            if not reset_token:
                return JsonResponse({"message": "  ."}, status=400)

            #  
            user_id, error_msg = PasswordResetSecurity.verify_reset_token(reset_token)
            if not user_id:
                return StandardResponse.validation_error({"email": error_msg})

            #   
            if len(password) < 8:
                return JsonResponse({"message": " 8  ."}, status=400)
            
            import re
            if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
                return JsonResponse({"message": "    ."}, status=400)

            user = models.User.objects.get_or_none(id=user_id)
            if user and user.username == email:
                user.set_password(password)
                user.save()
                logging.info(f"Password reset successful for user {email}")
                return JsonResponse({"message": "success"}, status=200)
            else:
                return JsonResponse({"message": "   ."}, status=403)
        except Exception as e:
            logger.error(f"Error in CheckEmail: {str(e)}", exc_info=True)
            return JsonResponse({"message": "     ."}, status=500)


class KakaoLogin(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            access_token = data.get("access_token")

            profile_request = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            kakao_user = profile_request.json()
            logger.debug(f"Kakao user data: {kakao_user}")

            kakao_id = kakao_user["id"]
            nickname = kakao_user.get("properties").get("nickname")
            email = kakao_user.get("kakao_account").get("email")
            # if not email:
            #     email = kakao_id
            if not email:
                return JsonResponse({"message": "  ."}, status=400)

            user, is_created = models.User.objects.get_or_create(username=email)

            if is_created:
                user.login_method = "kakao"
                user.nickname = nickname
                user.save()
            else:
                if user.login_method != "kakao":
                    return JsonResponse({"message": "  ."}, status=400)

            # SimpleJWT  
            refresh = RefreshToken.for_user(user)
            vridge_session = str(refresh.access_token)
            res = JsonResponse(
                {
                    "message": "success",
                    "vridge_session": vridge_session,
                    "refresh_token": str(refresh),
                    "user": user.username,
                },
                status=200,
            )
            res.set_cookie(
                "vridge_session",
                vridge_session,
                httponly=True,
                samesite="Lax",
                secure=True,
                max_age=2419200,
            )
            return res
        except Exception as e:
            logger.error(f"Error in CheckEmail: {str(e)}", exc_info=True)
            return JsonResponse({"message": "     ."}, status=500)


class NaverLogin(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            code = data.get("code")
            state = data.get("state")

            NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
            NAVER_SECRET_KEY = settings.NAVER_SECRET_KEY

            token_request = requests.post(
                f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&state={state}&client_id={NAVER_CLIENT_ID}&client_secret={NAVER_SECRET_KEY}&code={code}"
            )

            token_json = token_request.json()

            error = token_json.get("error", None)
            if error is not None:
                raise Exception("Can't get access token")

            access_token = token_json.get("access_token")

            profile_request = requests.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            profile_json = profile_request.json()
            logger.debug(f"Naver profile data: {profile_json}")

            response = profile_json.get("response")
            email = response.get("email", None)
            nickname = response.get("nickname", None)
            name = response.get("name", None)
            naver_id = response.get("id", None)
            if not email:
                return JsonResponse({"message": "  ."}, status=400)

            user, is_created = models.User.objects.get_or_create(username=email)

            if is_created:
                user.login_method = "naver"
                if nickname:
                    user.nickname = nickname
                else:
                    user.nickname = name
                user.save()
            else:
                if user.login_method != "naver":
                    return JsonResponse({"message": "  ."}, status=400)

            # SimpleJWT  
            refresh = RefreshToken.for_user(user)
            vridge_session = str(refresh.access_token)
            res = JsonResponse(
                {
                    "message": "success",
                    "vridge_session": vridge_session,
                    "refresh_token": str(refresh),
                    "user": user.username,
                },
                status=200,
            )
            res.set_cookie(
                "vridge_session",
                vridge_session,
                httponly=True,
                samesite="Lax",
                secure=True,
                max_age=2419200,
            )
            return res
        except Exception as e:
            logger.error(f"Error in CheckEmail: {str(e)}", exc_info=True)
            return JsonResponse({"message": "     ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class GoogleLogin(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            access_token = data.get("access_token")
            state = data.get("state")
            scopes = data.get("scopes")
            # credential = data.get("credential")

            # import base64, jwt
            # encoded_json = credential.split(".")[1]
            # decoded_bytes = base64.urlsafe_b64decode(encoded_json + "=" * (4 - len(encoded_json) % 4))
            # decoded_token = decoded_bytes.decode("utf-8")
            # print(decoded_token)

            if not state:
                return JsonResponse({"message": " ."}, status=400)

            # useinfo = requests.get(
            #     f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}&scopes={scopes}"
            # )
            useinfo = requests.get(
                f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}&scopes={scopes}"
            )

            userinfo = useinfo.json()
            logger.debug(f"Google userinfo: {userinfo}")

            email = userinfo.get("email")
            nickname = userinfo.get("name")
            ids = userinfo.get("id")
            if not email:
                return JsonResponse({"message": "  ."}, status=400)

            user, is_created = models.User.objects.get_or_create(username=email)
            if is_created:
                user.login_method = "google"
                user.nickname = nickname
                user.save()
            else:
                if user.login_method != "google":
                    return JsonResponse({"message": "  ."}, status=400)

            # SimpleJWT  
            refresh = RefreshToken.for_user(user)
            vridge_session = str(refresh.access_token)
            res = JsonResponse(
                {
                    "message": "success",
                    "vridge_session": vridge_session,
                    "refresh_token": str(refresh),
                    "user": user.username,
                },
                status=200,
            )
            res.set_cookie(
                "vridge_session",
                vridge_session,
                httponly=True,
                samesite="Lax",
                secure=True,
                max_age=2419200,
            )
            return res
        except Exception as e:
            logger.error(f"Error in CheckEmail: {str(e)}", exc_info=True)
            return JsonResponse({"message": "     ."}, status=500)


class UserMe(View):
    @user_validator
    def get(self, request):
        try:
            user = request.user
            
            #   URL 
            profile_image = None
            if hasattr(user, 'profile') and user.profile and user.profile.profile_image:
                #  URL 
                from django.conf import settings
                profile_image = user.profile.profile_image.url
                if profile_image and not profile_image.startswith('http'):
                    # Railway  HTTPS 
                    protocol = 'https' if not settings.DEBUG else 'http'
                    host = request.get_host()
                    profile_image = f"{protocol}://{host}{profile_image}"
            
            return JsonResponse({
                "id": user.id,
                "username": user.username,
                "email": user.username if user.login_method == "email" else "",
                "nickname": user.nickname if user.nickname else user.username,
                "login_method": user.login_method,
                "date_joined": user.date_joined.isoformat() if user.date_joined else None,
                "profile_image": profile_image,
            }, status=200)
        except Exception as e:
            logger.error(f"Error in UserMe: {str(e)}", exc_info=True)
            return StandardResponse.server_error()


class UserMemo(View):
    @user_validator
    def post(self, request):
        try:
            user = request.user

            data = json.loads(request.body)

            date = data.get("date")

            memo = data.get("memo")
            if date and memo:
                models.UserMemo.objects.create(user=user, date=date, memo=memo)

            return JsonResponse({"message": "success"}, status=200)

        except Exception as e:
            logger.error(f"Error in CheckEmail: {str(e)}", exc_info=True)
            return JsonResponse({"message": "     ."}, status=500)

    @user_validator
    def delete(self, request, id):
        try:
            user = request.user
            memo = models.UserMemo.objects.get_or_none(id=id)

            if memo is None:
                return JsonResponse({"message": "    ."}, status=404)

            if memo.user != user:
                return JsonResponse({"message": " ."}, status=403)

            memo.delete()

            return JsonResponse({"message": "success"}, status=200)
        except Exception as e:
            logger.error(f"Error in CheckEmail: {str(e)}", exc_info=True)
            return JsonResponse({"message": "     ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class NotificationView(View):
    """  """
    
    @user_validator
    def get(self, request):
        """  """
        try:
            user = request.user
            
            #     (projects  Notification  )
            from users.models import Notification as ProjectNotification
            unread_count = ProjectNotification.objects.filter(
                recipient=user,
                is_read=False
            ).count()
            
            # URL  
            unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
            limit = int(request.GET.get('limit', 20))
            
            #   (projects  Notification  )
            from users.models import Notification as ProjectNotification
            notifications_query = ProjectNotification.objects.filter(recipient=user)
            
            if unread_only:
                notifications_query = notifications_query.filter(is_read=False)
            
            notifications = notifications_query.order_by('-created')[:limit]
            
            notifications_data = [
                {
                    "id": notif.id,
                    "type": notif.notification_type,
                    "title": notif.title,
                    "message": notif.message,
                    "is_read": notif.is_read,
                    "created": notif.created.isoformat(),
                    "related_project": {
                        "id": notif.project_id,
                        "name": ""
                    } if notif.project_id else None,
                }
                for notif in notifications
            ]
            
            return JsonResponse({
                "unread_count": unread_count,
                "notifications": notifications_data
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in notification list: {str(e)}", exc_info=True)
            return JsonResponse({"message": "    ."}, status=500)
    
    @user_validator
    def post(self, request):
        """  """
        try:
            user = request.user
            data = json.loads(request.body)
            
            notification_id = data.get('notification_id')
            mark_all_read = data.get('mark_all_read', False)
            
            if mark_all_read:
                #    
                from django.utils import timezone
                models.Notification.objects.filter(
                    recipient=user,
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
                return JsonResponse({"message": "   ."}, status=200)
            
            elif notification_id:
                #    
                notification = models.Notification.objects.filter(
                    id=notification_id,
                    recipient=user
                ).first()
                
                if not notification:
                    return JsonResponse({"message": "   ."}, status=404)
                
                if not notification.is_read:
                    from django.utils import timezone
                    notification.is_read = True
                    notification.read_at = timezone.now()
                    notification.save()
                
                return JsonResponse({"message": "  ."}, status=200)
            
            else:
                return JsonResponse({"message": "notification_id  mark_all_read ."}, status=400)
            
        except Exception as e:
            logger.error(f"Error in notification mark read: {str(e)}", exc_info=True)
            return JsonResponse({"message": "    ."}, status=500)
    
    @user_validator
    def delete(self, request, notification_id):
        """ """
        try:
            user = request.user
            
            notification = models.Notification.objects.filter(
                id=notification_id,
                recipient=user
            ).first()
            
            if not notification:
                return JsonResponse({"message": "   ."}, status=404)
            
            notification.delete()
            return JsonResponse({"message": " ."}, status=200)
            
        except Exception as e:
            logger.error(f"Error in notification delete: {str(e)}", exc_info=True)
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UnreadNotificationCount(View):
    """    """
    
    @user_validator
    def get(self, request):
        """    """
        try:
            user = request.user
            from users.models import Notification as ProjectNotification
            
            unread_count = ProjectNotification.objects.filter(
                recipient=user,
                is_read=False
            ).count()
            
            return JsonResponse({
                "count": unread_count
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in unread notification count: {str(e)}")
            return JsonResponse({"message": "       ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MarkNotificationsRead(View):
    """   """
    
    @user_validator
    def post(self, request):
        """   """
        try:
            user = request.user
            data = json.loads(request.body)
            notification_ids = data.get('notification_ids', [])
            
            if not notification_ids:
                return JsonResponse({"message": "notification_ids ."}, status=400)
            
            from users.models import Notification as ProjectNotification
            from django.utils import timezone
            
            updated_count = ProjectNotification.objects.filter(
                id__in=notification_ids,
                recipient=user,
                is_read=False
            ).update(is_read=True)
            
            return JsonResponse({
                "message": f"{updated_count}   .",
                "updated_count": updated_count
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in mark notifications read: {str(e)}")
            return JsonResponse({"message": "     ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class NotificationDetail(View):
    """  """
    
    @user_validator
    def delete(self, request, notification_id):
        """ """
        try:
            user = request.user
            from users.models import Notification as ProjectNotification
            
            notification = ProjectNotification.objects.filter(
                id=notification_id,
                user=user
            ).first()
            
            if not notification:
                return JsonResponse({"message": "   ."}, status=404)
            
            notification.delete()
            return JsonResponse({"message": " ."}, status=200)
            
        except Exception as e:
            logger.error(f"Error in notification detail delete: {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


class RecentInvitationsView(View):
    """   """
    
    @user_validator
    def get(self, request):
        """    """
        try:
            user = request.user
            limit = int(request.GET.get('limit', 10))
            
            #    
            from django.db import connection
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'users_recentinvitation'
                        );
                    """)
                    table_exists = cursor.fetchone()[0]
                else:
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='users_recentinvitation';
                    """)
                    table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                logger.warning("users_recentinvitation table does not exist")
                return JsonResponse({
                    "status": "success",
                    "recent_invitations": []
                }, status=200)
            
            recent_invitations = models.RecentInvitation.objects.filter(
                inviter=user
            ).order_by('-last_invited_at')[:limit]
            
            invitations_data = []
            for invitation in recent_invitations:
                invitations_data.append({
                    "id": invitation.id,
                    "email": invitation.invitee_email,
                    "name": invitation.invitee_name or invitation.invitee_email.split('@')[0],
                    "project_name": invitation.project_name,
                    "invitation_count": invitation.invitation_count,
                    "last_invited_at": invitation.last_invited_at.isoformat() if invitation.last_invited_at else None
                })
            
            return JsonResponse({
                "status": "success",
                "recent_invitations": invitations_data
            }, status=200)
            
        except Exception as e:
            import traceback
            logger.error(f"Error in RecentInvitationsView: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                "message": "      .",
                "error": str(e),
                "type": type(e).__name__
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FriendshipView(View):
    """ """
    
    @user_validator
    def get(self, request):
        """  """
        try:
            user = request.user
            
            #    ()
            friendships = models.Friendship.objects.filter(
                models.Q(user=user) | models.Q(friend=user),
                status='accepted'
            ).select_related('user', 'friend', 'user__profile', 'friend__profile')
            
            friends_data = []
            for friendship in friendships:
                #    
                friend_user = friendship.friend if friendship.user == user else friendship.user
                
                friends_data.append({
                    "id": friendship.id,
                    "friend": {
                        "id": friend_user.id,
                        "email": friend_user.email,
                        "nickname": friend_user.nickname or friend_user.username,
                        "profile_image": friend_user.profile.profile_image.url if hasattr(friend_user, 'profile') and friend_user.profile.profile_image else None,
                        "company": friend_user.profile.company if hasattr(friend_user, 'profile') else '',
                        "position": friend_user.profile.position if hasattr(friend_user, 'profile') else '',
                    },
                    "since": friendship.responded_at.isoformat() if friendship.responded_at else friendship.created.isoformat()
                })
            
            #      
            response_data = {
                "friends": friends_data,
                "count": len(friends_data)
            }
            
            if len(friends_data) == 0:
                response_data["message"] = "  ."
            
            return JsonResponse(response_data, status=200)
            
        except Exception as e:
            logger.error(f"Error in friendship list: {str(e)}", exc_info=True)
            return JsonResponse({
                "message": "     .",
                "friends": [],
                "count": 0
            }, status=200)  # 500  200      
    
    @user_validator
    def post(self, request):
        """  """
        try:
            user = request.user
            data = json.loads(request.body)
            friend_email = data.get('friend_email')
            
            if not friend_email:
                return JsonResponse({"message": "  ."}, status=400)
            
            #      
            if friend_email == user.email:
                return JsonResponse({"message": "      ."}, status=400)
            
            #    
            try:
                friend_user = User.objects.get(email=friend_email)
            except User.DoesNotExist:
                return JsonResponse({"message": "     ."}, status=404)
            
            #     
            existing_friendship = models.Friendship.objects.filter(
                models.Q(user=user, friend=friend_user) | 
                models.Q(user=friend_user, friend=user)
            ).first()
            
            if existing_friendship:
                if existing_friendship.status == 'accepted':
                    return JsonResponse({"message": " ."}, status=400)
                elif existing_friendship.status == 'pending':
                    return JsonResponse({"message": "    ."}, status=400)
                elif existing_friendship.status == 'blocked':
                    return JsonResponse({"message": " ."}, status=400)
            
            #    ( )
            friendship1 = models.Friendship.objects.create(
                recipient=user,
                friend=friend_user,
                requested_by=user,
                status='pending'
            )
            
            friendship2 = models.Friendship.objects.create(
                user=friend_user,
                friend=user,
                requested_by=user,
                status='pending'
            )
            
            #   
            from users.models import Notification as ProjectNotification
            from projects.notification_service import NotificationService
            
            try:
                NotificationService.create_notification(
                    user=friend_user,
                    notification_type='FRIEND_REQUEST_RECEIVED',
                    title='  ',
                    message=f'{user.nickname or user.username}   .',
                    action_url=f'/friends/requests'
                )
            except Exception as e:
                logger.error(f"    : {str(e)}")
            
            return JsonResponse({
                "message": "  .",
                "friendship_id": friendship1.id
            }, status=201)
            
        except Exception as e:
            logger.error(f"Error in friend request: {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)
    
    @user_validator
    def delete(self, request):
        """ """
        try:
            user = request.user
            data = json.loads(request.body)
            friend_email = data.get('friend_email')
            
            if not friend_email:
                return JsonResponse({"message": "  ."}, status=400)
            
            #   
            try:
                friend_user = User.objects.get(email=friend_email)
            except User.DoesNotExist:
                return JsonResponse({"message": "     ."}, status=404)
            
            #     
            friendships = models.Friendship.objects.filter(
                models.Q(user=user, friend=friend_user) | 
                models.Q(user=friend_user, friend=user)
            )
            
            if not friendships.exists():
                return JsonResponse({"message": "   ."}, status=404)
            
            #     
            deleted_count = friendships.delete()[0]
            
            return JsonResponse({
                "message": f"{friend_user.nickname or friend_user.username}   .",
                "deleted_count": deleted_count
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in friend deletion: {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FriendRequestView(View):
    """   """
    
    @user_validator
    def get(self, request):
        """    """
        try:
            user = request.user
            
            #     (pending )
            friend_requests = models.Friendship.objects.filter(
                recipient=user,
                status='pending'
            ).select_related('requested_by', 'requested_by__profile')
            
            requests_data = []
            for friendship in friend_requests:
                requester = friendship.requested_by
                requests_data.append({
                    "id": friendship.id,
                    "requester": {
                        "id": requester.id,
                        "email": requester.email,
                        "nickname": requester.nickname or requester.username,
                        "profile_image": requester.profile.profile_image.url if hasattr(requester, 'profile') and requester.profile.profile_image else None,
                        "company": requester.profile.company if hasattr(requester, 'profile') else '',
                        "position": requester.profile.position if hasattr(requester, 'profile') else '',
                    },
                    "requested_at": friendship.created.isoformat()
                })
            
            #      
            response_data = {
                "requests": requests_data,
                "count": len(requests_data)
            }
            
            if len(requests_data) == 0:
                response_data["message"] = "   ."
            
            return JsonResponse(response_data, status=200)
            
        except Exception as e:
            logger.error(f"Error in friend requests: {str(e)}", exc_info=True)
            return JsonResponse({
                "message": "      .",
                "requests": [],
                "count": 0
            }, status=200)  # 500  200      


@method_decorator(csrf_exempt, name='dispatch')
class FriendRequestResponse(View):
    """  /"""
    
    @user_validator
    def post(self, request, friendship_id):
        """  """
        try:
            user = request.user
            data = json.loads(request.body)
            action = data.get('action')  # 'accept' or 'decline'
            
            if action not in ['accept', 'decline']:
                return JsonResponse({"message": " ."}, status=400)
            
            #   
            friendship = models.Friendship.objects.filter(
                id=friendship_id,
                recipient=user,
                status='pending'
            ).first()
            
            if not friendship:
                return JsonResponse({"message": "    ."}, status=404)
            
            from django.utils import timezone
            
            if action == 'accept':
                #    
                models.Friendship.objects.filter(
                    models.Q(user=user, friend=friendship.requested_by) |
                    models.Q(user=friendship.requested_by, friend=user)
                ).update(
                    status='accepted',
                    responded_at=timezone.now()
                )
                
                #  
                from projects.notification_service import NotificationService
                try:
                    NotificationService.create_notification(
                        user=friendship.requested_by,
                        notification_type='FRIEND_REQUEST_ACCEPTED',
                        title='  ',
                        message=f'{user.nickname or user.username}   .',
                        action_url=f'/friends'
                    )
                except Exception as e:
                    logger.error(f"    : {str(e)}")
                
                return JsonResponse({"message": "  ."}, status=200)
            
            else:  # decline
                #    
                models.Friendship.objects.filter(
                    models.Q(user=user, friend=friendship.requested_by) |
                    models.Q(user=friendship.requested_by, friend=user)
                ).update(
                    status='declined',
                    responded_at=timezone.now()
                )
                
                return JsonResponse({"message": "  ."}, status=200)
            
        except Exception as e:
            logger.error(f"Error in friend request response: {str(e)}")
            return JsonResponse({"message": "     ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FriendSearch(View):
    """ """
    
    @user_validator
    def get(self, request):
        """ """
        try:
            user = request.user
            query = request.GET.get('q', '').strip()
            
            if not query:
                return JsonResponse({"message": " ."}, status=400)
            
            #    
            users = User.objects.filter(
                models.Q(email__icontains=query) | 
                models.Q(nickname__icontains=query)
            ).exclude(id=user.id).select_related('profile')[:10]
            
            #    ID 
            friend_ids = set()
            friendships = models.Friendship.objects.filter(
                models.Q(user=user) | models.Q(friend=user),
                status__in=['pending', 'accepted']
            )
            
            for friendship in friendships:
                if friendship.user == user:
                    friend_ids.add(friendship.friend.id)
                else:
                    friend_ids.add(friendship.user.id)
            
            users_data = []
            for search_user in users:
                friendship_status = 'none'
                if search_user.id in friend_ids:
                    #   
                    friendship = models.Friendship.objects.filter(
                        models.Q(user=user, friend=search_user) | 
                        models.Q(user=search_user, friend=user)
                    ).first()
                    if friendship:
                        friendship_status = friendship.status
                
                users_data.append({
                    "id": search_user.id,
                    "email": search_user.email,
                    "nickname": search_user.nickname or search_user.username,
                    "profile_image": search_user.profile.profile_image.url if hasattr(search_user, 'profile') and search_user.profile.profile_image else None,
                    "company": search_user.profile.company if hasattr(search_user, 'profile') else '',
                    "position": search_user.profile.position if hasattr(search_user, 'profile') else '',
                    "friendship_status": friendship_status
                })
            
            return JsonResponse({
                "users": users_data,
                "count": len(users_data)
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in friend search: {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RecentInvitationView(View):
    """   """
    
    @user_validator
    def get(self, request):
        """    """
        try:
            user = request.user
            limit = int(request.GET.get('limit', 10))
            
            recent_invitations = models.RecentInvitation.objects.filter(
                inviter=user
            ).order_by('-last_invited_at')[:limit]
            
            invitations_data = []
            for invitation in recent_invitations:
                invitations_data.append({
                    "email": invitation.invitee_email,
                    "name": invitation.invitee_name,
                    "last_project": invitation.project_name,
                    "invitation_count": invitation.invitation_count,
                    "last_invited_at": invitation.last_invited_at.isoformat()
                })
            
            #      
            response_data = {
                "recent_invitations": invitations_data,
                "count": len(invitations_data)
            }
            
            if len(invitations_data) == 0:
                response_data["message"] = "   ."
            
            return JsonResponse(response_data, status=200)
            
        except Exception as e:
            logger.error(f"Error in recent invitations: {str(e)}", exc_info=True)
            return JsonResponse({
                "message": "      .",
                "recent_invitations": [],
                "count": 0
            }, status=200)  # 500  200      


@method_decorator(csrf_exempt, name='dispatch')
class EmailVerificationView(View):
    """  """
    
    def get(self, request, token):
        """   """
        try:
            from .email_verification_service import EmailVerificationService
            
            success, message = EmailVerificationService.verify_email(token)
            
            if success:
                #    ( )
                try:
                    from .models import EmailVerificationToken
                    verification_token = EmailVerificationToken.objects.get(token=token)
                    EmailVerificationService.send_welcome_email(verification_token.user)
                except Exception as e:
                    logger.warning(f"   : {str(e)}")
                
                return JsonResponse({
                    "success": True,
                    "message": message
                }, status=200)
            else:
                return JsonResponse({
                    "success": False,
                    "message": message
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error in email verification: {str(e)}")
            return JsonResponse({
                "success": False,
                "message": "    ."
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ResendVerificationEmailView(View):
    """  """
    
    def post(self, request):
        """  """
        try:
            data = json.loads(request.body)
            email = data.get("email")
            
            if not email:
                return JsonResponse({"message": "  ."}, status=400)
            
            #   
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return StandardResponse.validation_error({"email": error_msg})
            
            #   
            # N+1  :   
            user = models.User.objects.filter(username=email).first()
            if not user:
                return JsonResponse({"message": "  ."}, status=404)
            
            #    -  
            try:
                from .email_verification_service import EmailVerificationService
                success, message = EmailVerificationService.resend_verification_email(user)
                
                if success:
                    return JsonResponse({"message": message}, status=200)
                else:
                    return JsonResponse({"message": message}, status=400)
            except Exception as e:
                logger.error(f"   : {str(e)}")
                #  :     True 
                user.email_verified = True
                user.email_verified_at = timezone.now()
                user.save()
                return JsonResponse({
                    "message": "  .   .",
                    "verified": True
                }, status=200)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "  ."}, status=400)
        except Exception as e:
            logger.error(f"Error in resend verification email: {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CheckEmailVerificationStatusView(View):
    """   """
    
    def post(self, request):
        """   """
        try:
            data = json.loads(request.body)
            email = data.get("email")
            
            if not email:
                return JsonResponse({"message": "  ."}, status=400)
            
            #   
            # N+1  :   
            user = models.User.objects.filter(username=email).first()
            if not user:
                return JsonResponse({"message": "  ."}, status=404)
            
            #   
            return JsonResponse({
                "email_verified": user.email_verified,
                "verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
                "user": user.username,
                "nickname": user.nickname
            }, status=200)
                
        except json.JSONDecodeError:
            return JsonResponse({"message": "  ."}, status=400)
        except Exception as e:
            logger.error(f"Error in check email verification status: {str(e)}")
            return JsonResponse({"message": "     ."}, status=500)


#    ()
from .views_debug import JWTDebugView, AuthDebugView


@method_decorator(csrf_exempt, name='dispatch')
class FriendBlockView(View):
    """  """
    
    @user_validator
    def post(self, request):
        """ """
        try:
            user = request.user
            data = json.loads(request.body)
            friend_email = data.get('friend_email')
            
            if not friend_email:
                return JsonResponse({"message": "   ."}, status=400)
            
            #     
            if friend_email == user.email:
                return JsonResponse({"message": "    ."}, status=400)
            
            #   
            try:
                friend_user = User.objects.get(email=friend_email)
            except User.DoesNotExist:
                return JsonResponse({"message": "     ."}, status=404)
            
            #    
            friendship = models.Friendship.objects.filter(
                models.Q(user=user, friend=friend_user) | 
                models.Q(user=friend_user, friend=user)
            ).first()
            
            if friendship:
                #    
                models.Friendship.objects.filter(
                    models.Q(user=user, friend=friend_user) | 
                    models.Q(user=friend_user, friend=user)
                ).update(status='blocked', requested_by=user)
            else:
                #    
                models.Friendship.objects.create(
                    user=user,
                    friend=friend_user,
                    requested_by=user,
                    status='blocked'
                )
            
            return JsonResponse({
                "message": f"{friend_user.nickname or friend_user.username} ."
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in friend block: {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)
    
    @user_validator
    def delete(self, request):
        """  """
        try:
            user = request.user
            data = json.loads(request.body)
            friend_email = data.get('friend_email')
            
            if not friend_email:
                return JsonResponse({"message": "    ."}, status=400)
            
            #    
            try:
                friend_user = User.objects.get(email=friend_email)
            except User.DoesNotExist:
                return JsonResponse({"message": "     ."}, status=404)
            
            #     
            friendships = models.Friendship.objects.filter(
                models.Q(user=user, friend=friend_user) | 
                models.Q(user=friend_user, friend=user),
                status='blocked'
            )
            
            if not friendships.exists():
                return JsonResponse({"message": "   ."}, status=404)
            
            #   
            deleted_count = friendships.delete()[0]
            
            return JsonResponse({
                "message": f"{friend_user.nickname or friend_user.username}  .",
                "deleted_count": deleted_count
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error in friend unblock: {str(e)}")
            return JsonResponse({"message": "    ."}, status=500)
