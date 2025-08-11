"""
Optimized login view with better error handling and performance
"""
import logging
import json
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .validators import InputValidator
from core.response_handler import StandardResponse

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class OptimizedSignIn(View):
    """Optimized login view with caching and better error handling"""
    
    def post(self, request):
        try:
            # 1. Parse request body
            if not request.body:
                return StandardResponse.validation_error({
                    "message": "Request body is required"
                })
            
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return StandardResponse.validation_error({
                    "message": "Invalid JSON format"
                })
            
            email = data.get("email") or data.get("username")
            password = data.get("password")
            
            # 2. Validate input
            if not email or not password:
                return StandardResponse.validation_error({
                    "message": "Email and password are required"
                })
            
            # 3. Rate limiting check
            client_ip = self.get_client_ip(request)
            if not self.check_rate_limit(email, client_ip):
                return JsonResponse({
                    "message": "Too many login attempts. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED"
                }, status=429)
            
            # 4. Authenticate user (optimized query)
            user = self.authenticate_user(email, password)
            
            if not user:
                # Log failed attempt (without sensitive data)
                logger.warning(
                    "Failed login attempt",
                    extra={
                        'email_hash': hash(email),
                        'ip': client_ip
                    }
                )
                return JsonResponse({
                    "message": "Invalid email or password",
                    "error_code": "INVALID_CREDENTIALS"
                }, status=401)
            
            # 5. Check user status
            if not user.is_active:
                return JsonResponse({
                    "message": "Account is deactivated",
                    "error_code": "ACCOUNT_INACTIVE"
                }, status=403)
            
            # 6. Check email verification
            if hasattr(user, 'email_verified') and not user.email_verified:
                # Auto-verify for development/testing
                if request.META.get('HTTP_HOST', '').startswith('localhost'):
                    user.email_verified = True
                    user.email_verified_at = timezone.now()
                    user.save(update_fields=['email_verified', 'email_verified_at'])
                else:
                    return JsonResponse({
                        "message": "Please verify your email first",
                        "error_code": "EMAIL_NOT_VERIFIED",
                        "email": user.email
                    }, status=403)
            
            # 7. Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # 8. Update last login (async task would be better)
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # 9. Prepare response
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email or user.username,
                "nickname": user.nickname or user.username,
                "login_method": getattr(user, 'login_method', 'email'),
                "email_verified": getattr(user, 'email_verified', True)
            }
            
            response_data = {
                "message": "success",
                "status": "success",
                "access": access_token,
                "refresh": refresh_token,
                "access_token": access_token,  # Compatibility
                "refresh_token": refresh_token,
                "user": user_data
            }
            
            # 10. Clear rate limit on successful login
            self.clear_rate_limit(email, client_ip)
            
            # Log successful login (structured logging)
            logger.info(
                "Successful login",
                extra={
                    'user_id': user.id,
                    'login_method': user.login_method
                }
            )
            
            response = JsonResponse(response_data, status=200)
            
            # Set secure cookie in production
            if not request.META.get('HTTP_HOST', '').startswith('localhost'):
                response.set_cookie(
                    "vridge_session",
                    access_token,
                    httponly=True,
                    samesite="Lax",
                    secure=True,
                    max_age=3600,
                )
            
            return response
            
        except Exception as e:
            # Log error without exposing sensitive information
            logger.error(
                "Login error occurred",
                extra={'error_type': type(e).__name__},
                exc_info=True
            )
            return StandardResponse.server_error()
    
    def authenticate_user(self, email, password):
        """Authenticate user with optimized query"""
        # Try cache first (for frequently logging in users)
        cache_key = f"user_auth:{hash(email)}"
        cached_user_id = cache.get(cache_key)
        
        if cached_user_id:
            try:
                user = User.objects.select_related('profile').get(
                    id=cached_user_id,
                    is_active=True
                )
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                cache.delete(cache_key)
        
        # Single optimized query
        user = User.objects.select_related('profile').filter(
            models.Q(username=email) | models.Q(email=email),
            is_active=True,
            is_deleted=False  # Ensure not soft-deleted
        ).first()
        
        if user and user.check_password(password):
            # Cache successful authentication (5 minutes)
            cache.set(cache_key, user.id, 300)
            return user
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
    
    def check_rate_limit(self, email, ip):
        """Check rate limiting"""
        # Rate limit by email
        email_key = f"login_attempts:email:{hash(email)}"
        email_attempts = cache.get(email_key, 0)
        
        if email_attempts >= 5:
            return False
        
        # Rate limit by IP
        ip_key = f"login_attempts:ip:{ip}"
        ip_attempts = cache.get(ip_key, 0)
        
        if ip_attempts >= 10:
            return False
        
        # Increment counters
        cache.set(email_key, email_attempts + 1, 300)  # 5 minutes
        cache.set(ip_key, ip_attempts + 1, 300)
        
        return True
    
    def clear_rate_limit(self, email, ip):
        """Clear rate limiting on successful login"""
        cache.delete(f"login_attempts:email:{hash(email)}")
        cache.delete(f"login_attempts:ip:{ip}")