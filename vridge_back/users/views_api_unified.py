"""
Unified Authentication API Views
Arthur, Chief Architect - 2025-08-12

These views work with the UnifiedCORSMiddleware to provide authentication endpoints.
Views focus on business logic only - CORS is handled entirely by middleware.

Design Principles:
- Single Responsibility: Views handle authentication only
- No CORS logic in views - middleware handles it
- Consistent error responses
- Performance monitoring built-in
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import time
import logging
import json

from .models import User
from .serializers import (
    LoginRequestSerializer, UserDataSerializer,
    SignupRequestSerializer, EmailValidationSerializer, 
    NicknameValidationSerializer
)

logger = logging.getLogger(__name__)


class LoginRateThrottle(AnonRateThrottle):
    """Rate limiting for login attempts"""
    rate = '5/min'  # 5 attempts per minute
    

@method_decorator(csrf_exempt, name='dispatch')
class UnifiedLoginAPIView(APIView):
    """
    Unified login view that works with UnifiedCORSMiddleware.
    No CORS logic here - middleware handles all CORS headers.
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request, *args, **kwargs):
        """Handle login requests"""
        start_time = time.time()
        request_id = getattr(request, 'id', 'unknown')
        
        try:
            # Log the attempt
            origin = request.META.get('HTTP_ORIGIN', 'no-origin')
            logger.info(f"[{request_id}] Login attempt from {origin}")
            
            # Extract and validate data
            data = self.get_request_data(request)
            if not data:
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'No data provided'
                    }
                }, status=400)
            
            # Validate with serializer
            serializer = LoginRequestSerializer(data=data)
            if not serializer.is_valid():
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid input data',
                        'details': serializer.errors
                    }
                }, status=400)
            
            validated_data = serializer.validated_data
            email = validated_data['email']
            password = validated_data['password']
            
            logger.info(f"[{request_id}] Processing login for: {email}")
            
            # Authenticate user
            user = self.authenticate_user(email, password, request)
            
            if not user:
                logger.warning(f"Authentication failed for: {email}")
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'INVALID_CREDENTIALS',
                        'message': 'Invalid email or password'
                    }
                }, status=401)
            
            # Check user status
            if not user.is_active:
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'ACCOUNT_INACTIVE',
                        'message': 'Account is inactive. Please contact support.'
                    }
                }, status=403)
            
            # Generate tokens
            tokens = self.generate_tokens(user)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Prepare response
            user_data = UserDataSerializer(user).data
            
            response_data = {
                'success': True,
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'user': user_data,
                    'tokens': tokens
                },
                'performance': {
                    'response_time_ms': round((time.time() - start_time) * 1000, 2)
                },
                'request_id': request_id
            }
            
            logger.info(f"[{request_id}] Login successful for: {email}")
            
            return JsonResponse(response_data, status=200)
            
        except Exception as e:
            logger.error(f"[{request_id}] Login error: {e}", exc_info=True)
            
            return JsonResponse({
                'success': False,
                'status': 'error',
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'An error occurred during login',
                    'type': e.__class__.__name__
                },
                'request_id': request_id
            }, status=500)
    
    def get_request_data(self, request):
        """Extract data from either DRF Request or Django WSGIRequest"""
        try:
            # Try DRF Request.data first
            if hasattr(request, 'data'):
                return request.data
            
            # Fall back to parsing request.body
            if request.body:
                return json.loads(request.body.decode('utf-8'))
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting request data: {e}")
            return None
    
    def authenticate_user(self, email, password, request):
        """Authenticate user by email or username"""
        try:
            # Try direct username authentication first
            user = authenticate(request, username=email, password=password)
            
            if not user:
                # Try to find user by email and authenticate with username
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    logger.info(f"User not found by email: {email}")
                except User.MultipleObjectsReturned:
                    logger.error(f"Multiple users with email: {email}")
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def generate_tokens(self, user):
        """Generate JWT tokens for authenticated user"""
        try:
            refresh = RefreshToken.for_user(user)
            
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'expires_in': settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', 
                                                      timezone.timedelta(minutes=60)).total_seconds()
            }
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            raise


@method_decorator(csrf_exempt, name='dispatch')
class UnifiedSignupAPIView(APIView):
    """
    Unified signup view that works with UnifiedCORSMiddleware.
    No CORS logic here - middleware handles all CORS headers.
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    def post(self, request, *args, **kwargs):
        """Handle signup requests"""
        request_id = getattr(request, 'id', 'unknown')
        
        try:
            # Extract and validate data
            data = self.get_request_data(request)
            if not data:
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'INVALID_REQUEST',
                        'message': 'No data provided'
                    }
                }, status=400)
            
            # Validate with serializer
            serializer = SignupRequestSerializer(data=data)
            if not serializer.is_valid():
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid input data',
                        'details': serializer.errors
                    }
                }, status=400)
            
            # Create user
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            tokens = {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
            
            # Prepare response
            user_data = UserDataSerializer(user).data
            
            return JsonResponse({
                'success': True,
                'status': 'success',
                'message': 'Signup successful',
                'data': {
                    'user': user_data,
                    'tokens': tokens
                }
            }, status=201)
            
        except Exception as e:
            logger.error(f"[{request_id}] Signup error: {e}", exc_info=True)
            
            return JsonResponse({
                'success': False,
                'status': 'error',
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'An error occurred during signup',
                    'type': e.__class__.__name__
                }
            }, status=500)
    
    def get_request_data(self, request):
        """Extract data from either DRF Request or Django WSGIRequest"""
        try:
            if hasattr(request, 'data'):
                return request.data
            
            if request.body:
                return json.loads(request.body.decode('utf-8'))
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting request data: {e}")
            return None


class UserMeAPIView(APIView):
    """
    Get current user information.
    No CORS logic here - middleware handles all CORS headers.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get current user information"""
        try:
            user_data = UserDataSerializer(request.user).data
            
            return JsonResponse({
                'success': True,
                'status': 'success',
                'data': {
                    'user': user_data
                }
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}", exc_info=True)
            
            return JsonResponse({
                'success': False,
                'status': 'error',
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'An error occurred getting user information'
                }
            }, status=500)


class CheckEmailAPIView(APIView):
    """
    Check if email is available for registration.
    No CORS logic here - middleware handles all CORS headers.
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Check email availability"""
        try:
            # Extract data
            if hasattr(request, 'data'):
                data = request.data
            elif request.body:
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = {}
            
            # Validate
            serializer = EmailValidationSerializer(data=data)
            if not serializer.is_valid():
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid email format',
                        'details': serializer.errors
                    }
                }, status=400)
            
            email = serializer.validated_data['email']
            
            # Check if email exists
            exists = User.objects.filter(email=email).exists()
            
            return JsonResponse({
                'success': True,
                'status': 'success',
                'data': {
                    'email': email,
                    'available': not exists
                }
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error checking email: {e}", exc_info=True)
            
            return JsonResponse({
                'success': False,
                'status': 'error',
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'An error occurred checking email'
                }
            }, status=500)


class CheckNicknameAPIView(APIView):
    """
    Check if nickname is available for registration.
    No CORS logic here - middleware handles all CORS headers.
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Check nickname availability"""
        try:
            # Extract data
            if hasattr(request, 'data'):
                data = request.data
            elif request.body:
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = {}
            
            # Validate
            serializer = NicknameValidationSerializer(data=data)
            if not serializer.is_valid():
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid nickname format',
                        'details': serializer.errors
                    }
                }, status=400)
            
            nickname = serializer.validated_data['nickname']
            
            # Check if nickname exists
            exists = User.objects.filter(nickname=nickname).exists()
            
            return JsonResponse({
                'success': True,
                'status': 'success',
                'data': {
                    'nickname': nickname,
                    'available': not exists
                }
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error checking nickname: {e}", exc_info=True)
            
            return JsonResponse({
                'success': False,
                'status': 'error',
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'An error occurred checking nickname'
                }
            }, status=500)