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
        
        # 모든 에러 응답에 CORS 헤더 추가
        if error_response:
            self._add_cors_headers(request, error_response)
        
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
    
    def _add_cors_headers(self, request, response):
        """
        Add CORS headers to error responses to prevent CORS errors
        """
        # CORS 헤더 추가 (vlanet.net 포함)
        origin = request.META.get('HTTP_ORIGIN', '')
        allowed_origins = [
            'https://vlanet.net',
            'https://www.vlanet.net',
            'http://localhost:3000',
            'http://localhost:3001',
        ]
        
        # 개발 환경이거나 허용된 오리진인 경우
        from django.conf import settings
        if origin in allowed_origins or settings.DEBUG:
            response['Access-Control-Allow-Origin'] = origin if origin else '*'
        else:
            response['Access-Control-Allow-Origin'] = 'https://vlanet.net'
            
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken, X-Requested-With'
        return response
    
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
        # Railway 헬스체크 경로 - 통합 관리
        health_paths = ['/', '/health', '/health/', '/api/health/', '/api/health']
        
        # 헬스체크 요청 처리
        if request.path in health_paths and request.method in ['GET', 'HEAD']:
            # 상세한 헬스체크 응답
            from django.db import connection
            import time
            
            health_status = {
                'status': 'healthy',
                'timestamp': int(time.time()),
                'service': 'videoplanet-backend',
                'checks': {
                    'database': 'unknown',
                    'cache': 'unknown'
                }
            }
            
            # 데이터베이스 체크
            try:
                with connection.cursor() as cursor:
                    cursor.execute('SELECT 1')
                health_status['checks']['database'] = 'healthy'
            except:
                health_status['checks']['database'] = 'unhealthy'
                health_status['status'] = 'degraded'
            
            # 캐시 체크
            try:
                from django.core.cache import cache
                cache.set('health_check', True, 10)
                if cache.get('health_check'):
                    health_status['checks']['cache'] = 'healthy'
                else:
                    health_status['checks']['cache'] = 'unhealthy'
            except:
                health_status['checks']['cache'] = 'unhealthy'
            
            return JsonResponse(health_status, status=200)
        
        return None


class CORSDebugMiddleware(MiddlewareMixin):
    """Enhanced CORS middleware that ensures headers are always present, including on errors"""
    
    def process_response(self, request, response):
        origin = request.META.get('HTTP_ORIGIN', '')
        
        # Validate origin against allowed origins for security
        allowed_origins = [
            'https://vlanet.net',
            'https://www.vlanet.net',
            'https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app',
            'https://vlanet-v2-0.vercel.app',
            'http://localhost:3000',
            'http://localhost:3001',
        ]
        
        # Check against regex patterns for Vercel dynamic URLs
        import re
        origin_patterns = [
            r"^https://vlanet-v2-0-.*\.vercel\.app$",
            r"^https://.*-vlanets-projects\.vercel\.app$",
            r"^https://vlanet-.*\.vercel\.app$",
        ]
        
        is_valid_origin = False
        if origin in allowed_origins:
            is_valid_origin = True
        else:
            for pattern in origin_patterns:
                if re.match(pattern, origin):
                    is_valid_origin = True
                    break
        
        # Set CORS headers for valid origins or all origins in development
        from django.conf import settings
        if is_valid_origin or settings.DEBUG:
            response['Access-Control-Allow-Origin'] = origin if origin else '*'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Expose-Headers'] = 'Content-Type, X-CSRFToken, Content-Length, X-Request-ID'
            
            # Always set these headers for any response
            if request.method == 'OPTIONS':
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
                response['Access-Control-Allow-Headers'] = (
                    'accept, accept-encoding, authorization, content-type, dnt, origin, '
                    'user-agent, x-csrftoken, x-requested-with, cache-control, pragma, '
                    'x-idempotency-key'
                )
                response['Access-Control-Max-Age'] = '86400'
                response.status_code = 200
        
        # Add request ID for debugging
        import uuid
        if not response.has_header('X-Request-ID'):
            response['X-Request-ID'] = str(uuid.uuid4())[:8]
            
        return response
    
    def process_exception(self, request, exception):
        """Ensure CORS headers are set even when exceptions occur"""
        from django.http import JsonResponse
        import logging
        
        logger = logging.getLogger(__name__)
        logger.error(f"Exception in request: {exception}", exc_info=True)
        
        # Create error response with CORS headers
        response = JsonResponse({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal server error occurred',
                'status': 500
            }
        }, status=500)
        
        # Apply CORS headers
        return self.process_response(request, response)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Type Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Clickjacking protection
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'
        
        # HSTS for HTTPS requests
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Monitor API response times and log slow requests"""
    
    def process_request(self, request):
        """Mark request start time"""
        import time
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log response time and add performance headers"""
        import time
        import logging
        
        if hasattr(request, '_start_time'):
            response_time = time.time() - request._start_time
            response_time_ms = round(response_time * 1000, 2)
            
            # Add performance header
            response['X-Response-Time'] = f"{response_time_ms}ms"
            
            # Log slow requests (>200ms)
            if response_time_ms > 200:
                logger = logging.getLogger(__name__)
                logger.warning(f"Slow API request: {request.method} {request.path} - {response_time_ms}ms", extra={
                    'response_time_ms': response_time_ms,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code
                })
            
            # Log API metrics for monitoring
            if request.path.startswith('/api/'):
                logger = logging.getLogger('api.performance')
                logger.info(f"API {request.method} {request.path} - {response.status_code} - {response_time_ms}ms")
        
        return response