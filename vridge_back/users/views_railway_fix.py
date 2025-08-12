"""
Railway-Compatible Authentication API Views
Handles both DRF Request and Django WSGIRequest
Production-ready with comprehensive error handling
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import time
import logging
import json
import traceback

from .models import User
from .serializers import (
    LoginRequestSerializer, LoginResponseSerializer, UserDataSerializer,
    SignupRequestSerializer, EmailValidationSerializer, 
    NicknameValidationSerializer
)
from core.response_handler import StandardResponse
from .security_utils import PasswordResetSecurity

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    """Add request timing for performance monitoring"""
    @staticmethod
    def add_timing(request):
        request._start_time = time.time()


class LoginRateThrottle(AnonRateThrottle):
    """Custom rate limiting for login attempts"""
    scope = 'login'
    rate = '10/min'  # Increased for production


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    """
    Railway-Compatible Login API View
    
    Handles both DRF and Django request types
    Provides robust error handling for production
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    def get_request_data(self, request):
        """
        Extract data from either DRF Request or Django WSGIRequest
        """
        # Try DRF Request.data first
        if hasattr(request, 'data'):
            return request.data
        
        # Fall back to parsing Django WSGIRequest
        if request.method == 'POST':
            if request.content_type and 'json' in request.content_type:
                try:
                    return json.loads(request.body.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.error(f"Failed to parse JSON body: {str(e)}")
                    return {}
            else:
                # Form data
                return request.POST.dict()
        
        return {}
    
    def post(self, request):
        """
        Authenticate user and return JWT tokens
        Railway-compatible implementation
        """
        PerformanceMiddleware.add_timing(request)
        
        try:
            # Extract request data safely
            request_data = self.get_request_data(request)
            
            if not request_data:
                logger.error("No request data received")
                return self.create_error_response(
                    "INVALID_REQUEST",
                    "No data provided in request",
                    400,
                    request
                )
            
            logger.info(f"Login attempt with data keys: {list(request_data.keys())}")
            
            # Validate request data
            serializer = LoginRequestSerializer(data=request_data)
            if not serializer.is_valid():
                logger.warning(f"Invalid login data: {serializer.errors}")
                return self.create_error_response(
                    "VALIDATION_ERROR",
                    "Invalid login credentials format",
                    400,
                    request,
                    details=serializer.errors
                )
            
            validated_data = serializer.validated_data
            email = validated_data['email']
            password = validated_data['password']
            
            logger.info(f"Processing login for: {email}")
            
            # Rate limiting check
            client_ip = self.get_client_ip(request)
            rate_ok, rate_msg = self.check_rate_limit(client_ip, email)
            if not rate_ok:
                return self.create_error_response(
                    "RATE_LIMIT_EXCEEDED",
                    rate_msg,
                    429,
                    request
                )
            
            # Attempt authentication
            user = self.authenticate_user(email, password, request)
            
            if not user:
                logger.warning(f"Authentication failed for: {email}")
                return self.create_error_response(
                    "INVALID_CREDENTIALS",
                    "Invalid email or password",
                    401,
                    request
                )
            
            # Check user status
            if not user.is_active:
                logger.warning(f"Inactive account login attempt: {email}")
                return self.create_error_response(
                    "ACCOUNT_INACTIVE",
                    "Account is inactive. Please contact support.",
                    403,
                    request
                )
            
            # Handle email verification if required
            email_verification_response = self.check_email_verification(user, request)
            if email_verification_response:
                return email_verification_response
            
            # Generate tokens
            tokens = self.generate_tokens(user)
            
            # Update user login info
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Prepare response data
            user_serializer = UserDataSerializer(user)
            response_data = {
                **tokens,
                "user": user_serializer.data,
                "expires_in": int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
            }
            
            logger.info(f"Successful login for user: {user.username} (ID: {user.id})")
            
            return self.create_success_response(
                response_data,
                "Login successful",
                request
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return self.create_error_response(
                "INVALID_JSON",
                "Invalid JSON format in request body",
                400,
                request
            )
        except Exception as e:
            logger.error(f"Unexpected login error: {str(e)}\n{traceback.format_exc()}")
            return self.create_error_response(
                "SERVER_ERROR",
                "An unexpected error occurred. Please try again.",
                500,
                request
            )
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    
    def check_rate_limit(self, client_ip, email):
        """Check rate limiting"""
        try:
            rate_ok, rate_msg = PasswordResetSecurity.check_rate_limit(
                f"{client_ip}:{email}",
                "login_attempt",
                limit=10,
                window=300  # 5 minutes
            )
            return rate_ok, rate_msg
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            return True, ""  # Allow on error
    
    def authenticate_user(self, email, password, request):
        """
        Authenticate user by email or username
        Returns User object or None
        """
        user = None
        
        # Try direct username authentication first
        user = authenticate(request, username=email, password=password)
        
        if not user:
            # Try to find user by email and authenticate with username
            try:
                user_obj = User.objects.get(email=email)
                logger.info(f"Found user by email: {user_obj.username}")
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                logger.info(f"User not found by email: {email}")
            except User.MultipleObjectsReturned:
                logger.error(f"Multiple users with email: {email}")
        
        if not user:
            # Log detailed failure for debugging (but not to client)
            try:
                test_user = User.objects.filter(email=email).first() or User.objects.filter(username=email).first()
                if test_user:
                    logger.warning(f"User exists but auth failed: {test_user.username}, active={test_user.is_active}")
                else:
                    logger.info(f"User not found: {email}")
            except Exception as e:
                logger.error(f"Error during auth debugging: {e}")
        
        return user
    
    def check_email_verification(self, user, request):
        """Check if email verification is required"""
        # Skip email verification in development or Railway
        if settings.DEBUG or os.environ.get('RAILWAY_ENVIRONMENT'):
            if hasattr(user, 'email_verified') and not user.email_verified:
                user.email_verified = True
                if hasattr(user, 'email_verified_at'):
                    user.email_verified_at = timezone.now()
                user.save()
            return None
        
        # Production: check verification
        if hasattr(user, 'email_verified') and not user.email_verified:
            return self.create_error_response(
                "EMAIL_NOT_VERIFIED",
                "Email verification required. Please check your email for verification link.",
                403,
                request,
                details={"email": user.email, "verification_required": True}
            )
        
        return None
    
    def generate_tokens(self, user):
        """Generate JWT tokens for user"""
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "vridge_session": access_token,  # For compatibility
                "access": access_token,  # Legacy compatibility
                "refresh": refresh_token,  # Legacy compatibility
            }
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            raise
    
    def create_success_response(self, data, message, request):
        """Create standardized success response"""
        response_data = {
            "success": True,
            "status": "success",
            "message": message,
            "data": data
        }
        
        # Add performance metrics
        if hasattr(request, '_start_time'):
            response_data['performance'] = {
                'response_time_ms': round((time.time() - request._start_time) * 1000, 2)
            }
        
        response_data['timestamp'] = time.time()
        
        return JsonResponse(response_data, status=200)
    
    def create_error_response(self, error_code, message, status_code, request, details=None):
        """Create standardized error response"""
        response_data = {
            "success": False,
            "status": "error",
            "error": {
                "code": error_code,
                "message": message,
                "status": status_code
            }
        }
        
        if details:
            response_data["error"]["details"] = details
        
        # Add performance metrics
        if hasattr(request, '_start_time'):
            response_data['performance'] = {
                'response_time_ms': round((time.time() - request._start_time) * 1000, 2)
            }
        
        response_data['timestamp'] = time.time()
        
        return JsonResponse(response_data, status=status_code)


import os

@method_decorator(csrf_exempt, name='dispatch')
class SignupAPIView(APIView):
    """Railway-Compatible Signup API View"""
    
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    def get_request_data(self, request):
        """Extract data from either DRF Request or Django WSGIRequest"""
        if hasattr(request, 'data'):
            return request.data
        
        if request.method == 'POST':
            if request.content_type and 'json' in request.content_type:
                try:
                    return json.loads(request.body.decode('utf-8'))
                except:
                    return {}
            else:
                return request.POST.dict()
        
        return {}
    
    def post(self, request):
        """Register new user account"""
        PerformanceMiddleware.add_timing(request)
        
        try:
            request_data = self.get_request_data(request)
            
            serializer = SignupRequestSerializer(data=request_data)
            if not serializer.is_valid():
                return JsonResponse({
                    "success": False,
                    "status": "error",
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid registration data",
                        "details": serializer.errors
                    }
                }, status=400)
            
            # Create user
            user = serializer.save()
            
            # Generate tokens for immediate login
            login_view = LoginAPIView()
            tokens = login_view.generate_tokens(user)
            user_serializer = UserDataSerializer(user)
            
            response_data = {
                **tokens,
                "user": user_serializer.data,
                "expires_in": int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
            }
            
            return JsonResponse({
                "success": True,
                "status": "success",
                "message": "Account created successfully",
                "data": response_data
            }, status=201)
            
        except Exception as e:
            logger.error(f"Signup error: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "status": "error",
                "error": {
                    "code": "SIGNUP_ERROR",
                    "message": "An error occurred during registration. Please try again.",
                    "status": 500
                }
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CheckEmailAPIView(APIView):
    """Railway-Compatible Email Availability Check"""
    
    permission_classes = [AllowAny]
    
    def get_request_data(self, request):
        """Extract data from either DRF Request or Django WSGIRequest"""
        if hasattr(request, 'data'):
            return request.data
        
        if request.method == 'POST':
            if request.content_type and 'json' in request.content_type:
                try:
                    return json.loads(request.body.decode('utf-8'))
                except:
                    return {}
            else:
                return request.POST.dict()
        
        return {}
    
    def post(self, request):
        """Check if email is available for registration"""
        PerformanceMiddleware.add_timing(request)
        
        try:
            request_data = self.get_request_data(request)
            
            serializer = EmailValidationSerializer(data=request_data)
            if not serializer.is_valid():
                return JsonResponse({
                    "success": False,
                    "status": "error",
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid email format",
                        "details": serializer.errors
                    }
                }, status=400)
            
            email = serializer.validated_data['email']
            
            # Check if email exists
            exists = User.objects.filter(email=email).exists()
            
            if exists:
                return JsonResponse({
                    "success": False,
                    "status": "error",
                    "error": {
                        "code": "EMAIL_EXISTS",
                        "message": "User with this email already exists",
                        "status": 409
                    }
                }, status=409)
            
            return JsonResponse({
                "success": True,
                "status": "success",
                "message": "Email is available"
            }, status=200)
            
        except Exception as e:
            logger.error(f"Email check error: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "status": "error",
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "An error occurred while checking email availability",
                    "status": 500
                }
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CheckNicknameAPIView(APIView):
    """Railway-Compatible Nickname Availability Check"""
    
    permission_classes = [AllowAny]
    
    def get_request_data(self, request):
        """Extract data from either DRF Request or Django WSGIRequest"""
        if hasattr(request, 'data'):
            return request.data
        
        if request.method == 'POST':
            if request.content_type and 'json' in request.content_type:
                try:
                    return json.loads(request.body.decode('utf-8'))
                except:
                    return {}
            else:
                return request.POST.dict()
        
        return {}
    
    def post(self, request):
        """Check if nickname is available"""
        PerformanceMiddleware.add_timing(request)
        
        try:
            request_data = self.get_request_data(request)
            
            serializer = NicknameValidationSerializer(data=request_data)
            if not serializer.is_valid():
                return JsonResponse({
                    "success": False,
                    "status": "error",
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid nickname format",
                        "details": serializer.errors
                    }
                }, status=400)
            
            nickname = serializer.validated_data['nickname']
            
            # Check if nickname exists
            exists = User.objects.filter(nickname=nickname).exists()
            
            if exists:
                return JsonResponse({
                    "success": False,
                    "status": "error",
                    "error": {
                        "code": "NICKNAME_EXISTS",
                        "message": "This nickname is already taken",
                        "status": 409
                    }
                }, status=409)
            
            return JsonResponse({
                "success": True,
                "status": "success",
                "message": "Nickname is available"
            }, status=200)
            
        except Exception as e:
            logger.error(f"Nickname check error: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "status": "error",
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "An error occurred while checking nickname availability",
                    "status": 500
                }
            }, status=500)


class UserMeAPIView(APIView):
    """Get current user information"""
    
    def get(self, request):
        """Get current authenticated user data"""
        PerformanceMiddleware.add_timing(request)
        
        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    "success": False,
                    "status": "error",
                    "error": {
                        "code": "AUTH_REQUIRED",
                        "message": "Authentication required",
                        "status": 401
                    }
                }, status=401)
            
            serializer = UserDataSerializer(request.user)
            
            return JsonResponse({
                "success": True,
                "status": "success",
                "message": "User data retrieved successfully",
                "data": serializer.data
            }, status=200)
            
        except Exception as e:
            logger.error(f"User data retrieval error: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "status": "error",
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "An error occurred while retrieving user data",
                    "status": 500
                }
            }, status=500)