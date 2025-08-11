"""
Performance optimization and error handling middleware
"""
import time
import logging
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import (
    PermissionDenied, 
    ValidationError, 
    ObjectDoesNotExist,
    SuspiciousOperation
)
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    MethodNotAllowed,
    ParseError,
    UnsupportedMediaType,
    Throttled
)
import json

logger = logging.getLogger(__name__)


class GlobalErrorHandlingMiddleware(MiddlewareMixin):
    """
    Global error handler to prevent 500 errors from exposing internal details.
    Provides user-friendly error messages and proper logging.
    """
    
    def process_exception(self, request, exception):
        """
        Handle exceptions globally and return safe error responses.
        """
        # 개발 환경과 프로덕션 환경 구분
        is_debug = getattr(settings, 'DEBUG', False)
        
        # 에러 타입별 처리
        error_response = self._get_error_response(exception, is_debug)
        
        # 로깅 레벨 결정
        log_level = self._get_log_level(exception)
        
        # 에러 로깅
        self._log_error(request, exception, log_level, is_debug)
        
        return error_response
    
    def _get_error_response(self, exception, is_debug):
        """
        Generate appropriate error response based on exception type.
        """
        # 404 Not Found
        if isinstance(exception, (Http404, ObjectDoesNotExist, NotFound)):
            return JsonResponse({
                'error': 'Not Found',
                'message': '요청하신 리소스를 찾을 수 없습니다.',
                'status_code': 404
            }, status=404)
        
        # 401 Authentication Failed
        if isinstance(exception, (AuthenticationFailed, NotAuthenticated)):
            return JsonResponse({
                'error': 'Authentication Required',
                'message': '인증이 필요합니다. 로그인 후 다시 시도해주세요.',
                'status_code': 401
            }, status=401)
        
        # 403 Permission Denied
        if isinstance(exception, PermissionDenied):
            return JsonResponse({
                'error': 'Permission Denied',
                'message': '이 작업을 수행할 권한이 없습니다.',
                'status_code': 403
            }, status=403)
        
        # 400 Bad Request - Validation Errors
        if isinstance(exception, ValidationError):
            errors = {}
            if hasattr(exception, 'message_dict'):
                errors = exception.message_dict
            elif hasattr(exception, 'messages'):
                errors = {'detail': exception.messages}
            else:
                errors = {'detail': str(exception)}
            
            return JsonResponse({
                'error': 'Validation Error',
                'message': '입력 데이터를 확인해주세요.',
                'errors': errors,
                'status_code': 400
            }, status=400)
        
        # 400 Bad Request - Parse Error
        if isinstance(exception, ParseError):
            return JsonResponse({
                'error': 'Parse Error',
                'message': '요청 데이터 형식이 올바르지 않습니다.',
                'status_code': 400
            }, status=400)
        
        # 405 Method Not Allowed
        if isinstance(exception, MethodNotAllowed):
            return JsonResponse({
                'error': 'Method Not Allowed',
                'message': f'이 엔드포인트는 {exception.detail} 메소드를 지원하지 않습니다.',
                'status_code': 405
            }, status=405)
        
        # 415 Unsupported Media Type
        if isinstance(exception, UnsupportedMediaType):
            return JsonResponse({
                'error': 'Unsupported Media Type',
                'message': '지원하지 않는 미디어 타입입니다.',
                'status_code': 415
            }, status=415)
        
        # 429 Too Many Requests
        if isinstance(exception, Throttled):
            wait_time = None
            if hasattr(exception, 'wait'):
                wait_time = int(exception.wait)
            
            return JsonResponse({
                'error': 'Too Many Requests',
                'message': '요청 횟수가 제한을 초과했습니다. 잠시 후 다시 시도해주세요.',
                'retry_after': wait_time,
                'status_code': 429
            }, status=429)
        
        # 400 Suspicious Operation
        if isinstance(exception, SuspiciousOperation):
            return JsonResponse({
                'error': 'Bad Request',
                'message': '잘못된 요청입니다.',
                'status_code': 400
            }, status=400)
        
        # DRF API Exception (Generic)
        if isinstance(exception, APIException):
            status_code = getattr(exception, 'status_code', 500)
            return JsonResponse({
                'error': getattr(exception, 'default_detail', 'API Error'),
                'message': str(exception),
                'status_code': status_code
            }, status=status_code)
        
        # 500 Internal Server Error - 기타 모든 예외
        if is_debug:
            # 개발 환경에서는 상세 정보 제공
            return JsonResponse({
                'error': 'Internal Server Error',
                'message': '서버 내부 오류가 발생했습니다.',
                'debug_info': {
                    'exception_type': type(exception).__name__,
                    'exception_message': str(exception),
                    'traceback': traceback.format_exc()
                },
                'status_code': 500
            }, status=500)
        else:
            # 프로덕션 환경에서는 안전한 메시지만 제공
            return JsonResponse({
                'error': 'Internal Server Error',
                'message': '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
                'status_code': 500
            }, status=500)
    
    def _get_log_level(self, exception):
        """
        Determine appropriate log level based on exception type.
        """
        # 클라이언트 에러 (4xx)는 WARNING
        if isinstance(exception, (
            Http404, ObjectDoesNotExist, NotFound,
            AuthenticationFailed, NotAuthenticated,
            PermissionDenied, ValidationError,
            ParseError, MethodNotAllowed,
            UnsupportedMediaType, SuspiciousOperation
        )):
            return logging.WARNING
        
        # Rate limiting은 INFO
        if isinstance(exception, Throttled):
            return logging.INFO
        
        # 서버 에러 (5xx)는 ERROR
        return logging.ERROR
    
    def _log_error(self, request, exception, log_level, is_debug):
        """
        Log error with appropriate context.
        """
        # 요청 정보 수집
        request_info = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            'ip': self._get_client_ip(request),
        }
        
        # 에러 정보 수집
        error_info = {
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
        }
        
        # 로그 메시지 구성
        log_message = (
            f"Error handling request: {request_info['method']} {request_info['path']} "
            f"by {request_info['user']} from {request_info['ip']}. "
            f"Exception: {error_info['exception_type']}: {error_info['exception_message']}"
        )
        
        # 로깅
        if log_level == logging.ERROR:
            # 서버 에러는 전체 traceback 포함
            logger.error(log_message, exc_info=True, extra={
                'request_info': request_info,
                'error_info': error_info
            })
        else:
            # 클라이언트 에러는 간단한 로그만
            logger.log(log_level, log_message, extra={
                'request_info': request_info,
                'error_info': error_info
            })
    
    def _get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip


class PerformanceMiddleware(MiddlewareMixin):
    """Log request processing time"""
    
    def process_request(self, request):
        request._start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            if duration > 1.0:  # Log slow requests
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s"
                )
        return response


class CacheMiddleware(MiddlewareMixin):
    """Simple cache middleware for GET requests"""
    
    def process_request(self, request):
        if request.method == 'GET' and request.path.startswith('/api/'):
            cache_key = f"response:{request.path}:{request.GET.urlencode()}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return HttpResponse(
                    cached_response['content'],
                    content_type=cached_response['content_type'],
                    status=cached_response['status']
                )
    
    def process_response(self, request, response):
        if (request.method == 'GET' and 
            request.path.startswith('/api/') and
            response.status_code == 200 and
            'feedback' not in request.path):  # Don't cache feedback data
            
            cache_key = f"response:{request.path}:{request.GET.urlencode()}"
            cache.set(cache_key, {
                'content': response.content,
                'content_type': response.get('Content-Type', 'application/json'),
                'status': response.status_code
            }, 300)  # Cache for 5 minutes
        
        return response


class RailwayHealthCheckMiddleware(MiddlewareMixin):
    """Handle Railway health checks without host validation"""
    
    def process_request(self, request):
        # Railway    -   
        health_paths = ['/', '/health', '/health/', '/api/health/', '/api/health']
        
        #    OK  (Railway  User-Agent   )
        if request.path in health_paths and request.method == 'GET':
            return JsonResponse({
                'status': 'ok'
            }, status=200)
        return None


class CORSDebugMiddleware(MiddlewareMixin):
    """Debug and ensure CORS headers are properly set"""
    
    def process_response(self, request, response):
        #   CORS     
        origin = request.META.get('HTTP_ORIGIN')
        
        # OPTIONS    
        if request.method == 'OPTIONS':
            if not response.has_header('Access-Control-Allow-Origin'):
                response['Access-Control-Allow-Origin'] = origin or '*'
            if not response.has_header('Access-Control-Allow-Methods'):
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            if not response.has_header('Access-Control-Allow-Headers'):
                response['Access-Control-Allow-Headers'] = 'accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with, cache-control, pragma'
            if not response.has_header('Access-Control-Allow-Credentials'):
                response['Access-Control-Allow-Credentials'] = 'true'
            if not response.has_header('Access-Control-Max-Age'):
                response['Access-Control-Max-Age'] = '86400'
        
        #    CORS  
        if origin and not response.has_header('Access-Control-Allow-Origin'):
            # corsheaders     
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # XSS 
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Type  
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Clickjacking  ( Django    )
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'
        
        # HSTS (HTTPS )
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy ( Feature Policy)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://accounts.google.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "img-src 'self' data: https: blob:",
            "font-src 'self' data: https://fonts.gstatic.com",
            "connect-src 'self' https://api.vlanet.net https://videoplanet.up.railway.app wss://videoplanet.up.railway.app",
            "media-src 'self' blob: data:",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        return response