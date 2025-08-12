"""
Enhanced Authentication API Views
Provides robust, secure, and standardized authentication endpoints
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
# from drf_yasg.utils import swagger_auto_schema  # Commented out - not installed
import time
import logging
import json

from .models import User
from .serializers import (
    LoginRequestSerializer, LoginResponseSerializer, UserDataSerializer,
    SignupRequestSerializer, EmailValidationSerializer, 
    NicknameValidationSerializer
)
from core.response_handler import StandardResponse
from .security_utils import PasswordResetSecurity
# Commented out - drf_yasg not installed
# from .api_docs import (
#     login_swagger_schema, signup_swagger_schema, check_email_swagger_schema,
#     check_nickname_swagger_schema, user_me_swagger_schema
# )

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    """Add request timing for performance monitoring"""
    @staticmethod
    def add_timing(request):
        request._start_time = time.time()


class LoginRateThrottle(AnonRateThrottle):
    """Custom rate limiting for login attempts"""
    scope = 'login'
    rate = '5/min'  # 5 attempts per minute


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    """
    Enhanced Login API View
    
    Provides secure authentication with comprehensive validation,
    rate limiting, and standardized responses.
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    # @login_swagger_schema  # Commented out - drf_yasg not installed
    def post(self, request):
        """
        Authenticate user and return JWT tokens
        
        Request Body:
        {
            "email": "user@example.com",  // Email or username
            "password": "password123"
        }
        
        Response:
        {
            "success": true,
            "status": "success", 
            "message": "Login successful",
            "data": {
                "access_token": "jwt_token...",
                "refresh_token": "jwt_token...",
                "vridge_session": "jwt_token...",
                "user": {...},
                "expires_in": 3600
            },
            "performance": {
                "response_time_ms": 150.5
            },
            "timestamp": 1691234567.123,
            "request_id": "abc12345"
        }
        """
        PerformanceMiddleware.add_timing(request)
        
        try:
            # Parse and validate request
            serializer = LoginRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return StandardResponse.validation_error(
                    errors=serializer.errors,
                    message="Invalid login credentials format"
                )
            
            validated_data = serializer.validated_data
            email = validated_data['email']
            password = validated_data['password']
            
            logger.info(f"Login attempt for: {email}")
            
            # Rate limiting check (additional to DRF throttling)
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            rate_ok, rate_msg = PasswordResetSecurity.check_rate_limit(
                f"{client_ip}:{email}",
                "login_attempt",
                limit=10,
                window=300  # 5 minutes
            )
            if not rate_ok:
                return StandardResponse.error(
                    "RATE_LIMIT_EXCEEDED",
                    rate_msg,
                    429,
                    request=request
                )
            
            # Attempt authentication
            user = self._authenticate_user(email, password, request)
            
            if not user:
                return StandardResponse.error(
                    "INVALID_CREDENTIALS",
                    "Invalid email or password",
                    401,
                    request=request
                )
            
            # Check user status
            if not user.is_active:
                return StandardResponse.error(
                    "ACCOUNT_INACTIVE",
                    "Account is inactive. Please contact support.",
                    403,
                    request=request
                )
            
            # Handle email verification if required
            email_verification_response = self._check_email_verification(user, request)
            if email_verification_response:
                return email_verification_response
            
            # Generate tokens
            tokens = self._generate_tokens(user)
            
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
            
            return StandardResponse.success(
                data=response_data,
                message="Login successful",
                request=request
            )
            
        except json.JSONDecodeError:
            return StandardResponse.error(
                "INVALID_JSON",
                "Invalid JSON format in request body",
                400,
                request=request
            )
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return StandardResponse.error(
                "LOGIN_ERROR",
                "An error occurred during login. Please try again.",
                500,
                request=request
            )
    
    def _authenticate_user(self, email, password, request):
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
    
    def _check_email_verification(self, user, request):
        """Check if email verification is required"""
        if not hasattr(user, 'email_verified') or user.email_verified:
            return None
        
        # In development or if no verification timestamp, auto-verify
        if settings.DEBUG or not hasattr(user, 'email_verified_at') or user.email_verified_at is None:
            logger.info(f"Auto-verifying email for development: {user.email}")
            user.email_verified = True
            user.email_verified_at = timezone.now()
            user.save(update_fields=['email_verified', 'email_verified_at'])
            return None
        
        # Production: require verification
        return StandardResponse.error(
            "EMAIL_NOT_VERIFIED",
            "Email verification required. Please check your email for verification link.",
            403,
            details={"email": user.email, "verification_required": True},
            request=request
        )
    
    def _generate_tokens(self, user):
        """Generate JWT tokens for user"""
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


@method_decorator(csrf_exempt, name='dispatch')
class SignupAPIView(APIView):
    """Enhanced Signup API View"""
    
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    # @signup_swagger_schema  # Commented out - drf_yasg not installed
    def post(self, request):
        """
        Register new user account
        
        Request Body:
        {
            "email": "user@example.com",
            "username": "username",
            "nickname": "Display Name",
            "password": "password123",
            "password_confirm": "password123"
        }
        """
        PerformanceMiddleware.add_timing(request)
        
        try:
            serializer = SignupRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return StandardResponse.validation_error(
                    errors=serializer.errors,
                    message="Invalid registration data"
                )
            
            # Create user
            user = serializer.save()
            
            # Generate tokens for immediate login
            tokens = LoginAPIView()._generate_tokens(user)
            user_serializer = UserDataSerializer(user)
            
            response_data = {
                **tokens,
                "user": user_serializer.data,
                "expires_in": int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
            }
            
            return StandardResponse.success(
                data=response_data,
                message="Account created successfully",
                status_code=201,
                request=request
            )
            
        except Exception as e:
            logger.error(f"Signup error: {str(e)}", exc_info=True)
            return StandardResponse.error(
                "SIGNUP_ERROR",
                "An error occurred during registration. Please try again.",
                500,
                request=request
            )


@method_decorator(csrf_exempt, name='dispatch')
class CheckEmailAPIView(APIView):
    """Enhanced Email Availability Check"""
    
    permission_classes = [AllowAny]
    
    # @check_email_swagger_schema  # Commented out - drf_yasg not installed
    def post(self, request):
        """Check if email is available for registration"""
        PerformanceMiddleware.add_timing(request)
        
        try:
            serializer = EmailValidationSerializer(data=request.data)
            if not serializer.is_valid():
                return StandardResponse.validation_error(
                    errors=serializer.errors,
                    message="Invalid email format"
                )
            
            email = serializer.validated_data['email']
            
            # Check if email exists
            exists = User.objects.filter(username=email).exists()
            
            if exists:
                return StandardResponse.error(
                    "EMAIL_EXISTS",
                    "User with this email already exists",
                    409,
                    request=request
                )
            
            return StandardResponse.success(
                message="Email is available",
                request=request
            )
            
        except Exception as e:
            logger.error(f"Email check error: {str(e)}", exc_info=True)
            return StandardResponse.server_error(request=request)


@method_decorator(csrf_exempt, name='dispatch')
class CheckNicknameAPIView(APIView):
    """Enhanced Nickname Availability Check"""
    
    permission_classes = [AllowAny]
    
    # @check_nickname_swagger_schema  # Commented out - drf_yasg not installed
    def post(self, request):
        """Check if nickname is available"""
        PerformanceMiddleware.add_timing(request)
        
        try:
            serializer = NicknameValidationSerializer(data=request.data)
            if not serializer.is_valid():
                return StandardResponse.validation_error(
                    errors=serializer.errors,
                    message="Invalid nickname format"
                )
            
            nickname = serializer.validated_data['nickname']
            
            # Check if nickname exists
            exists = User.objects.filter(nickname=nickname).exists()
            
            if exists:
                return StandardResponse.error(
                    "NICKNAME_EXISTS",
                    "This nickname is already taken",
                    409,
                    request=request
                )
            
            return StandardResponse.success(
                message="Nickname is available",
                request=request
            )
            
        except Exception as e:
            logger.error(f"Nickname check error: {str(e)}", exc_info=True)
            return StandardResponse.server_error(request=request)


class UserMeAPIView(APIView):
    """Get current user information"""
    
    # @user_me_swagger_schema  # Commented out - drf_yasg not installed
    def get(self, request):
        """Get current authenticated user data"""
        PerformanceMiddleware.add_timing(request)
        
        try:
            if not request.user.is_authenticated:
                return StandardResponse.unauthorized(
                    message="Authentication required",
                    request=request
                )
            
            serializer = UserDataSerializer(request.user)
            
            return StandardResponse.success(
                data=serializer.data,
                message="User data retrieved successfully",
                request=request
            )
            
        except Exception as e:
            logger.error(f"User data retrieval error: {str(e)}", exc_info=True)
            return StandardResponse.server_error(request=request)