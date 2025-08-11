"""
Enhanced CORS and Error Handling Middleware
API Developer Noah가 제공
"""

import json
import time
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from corsheaders.middleware import CorsMiddleware as BaseCorsMiddleware

logger = logging.getLogger(__name__)

class EnhancedCorsMiddleware(BaseCorsMiddleware):
    """CORS 헤더를 500 에러에서도 반환하는 미들웨어"""
    
    def process_response(self, request, response):
        """모든 응답에 CORS 헤더 추가"""
        # 기본 CORS 처리
        response = super().process_response(request, response)
        
        # 500 에러인 경우에도 CORS 헤더 추가
        if response.status_code >= 500:
            origin = request.META.get('HTTP_ORIGIN')
            if origin and self.origin_found_in_white_lists(origin, request):
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
        
        return response
    
    def process_exception(self, request, exception):
        """예외 발생 시 CORS 헤더 포함한 에러 응답"""
        logger.error(f"Exception in request: {exception}", exc_info=True)
        
        response = JsonResponse({
            'success': False,
            'error': {
                'message': 'Internal server error',
                'type': 'ServerError'
            }
        }, status=500)
        
        # CORS 헤더 추가
        origin = request.META.get('HTTP_ORIGIN')
        if origin:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
        
        return response

class PerformanceMiddleware(MiddlewareMixin):
    """API 성능 모니터링 미들웨어"""
    
    def process_request(self, request):
        """요청 시작 시간 기록"""
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """응답 시간 측정 및 로깅"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # 응답 헤더에 성능 정보 추가
            response['X-Response-Time'] = f"{duration:.3f}s"
            
            # 느린 요청 로깅
            if duration > 1.0:  # 1초 이상
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.3f}s"
                )
            
            # 성능 메트릭 수집 (옵션)
            if duration > 0.2 and request.path.startswith('/api/'):
                logger.info(
                    f"API Performance: {request.method} {request.path} "
                    f"- {duration:.3f}s - Status: {response.status_code}"
                )
        
        return response

class RateLimitMiddleware(MiddlewareMixin):
    """Rate Limiting 미들웨어"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}
        self.cleanup_interval = 60  # 1분마다 캐시 정리
        self.last_cleanup = time.time()
    
    def get_client_ip(self, request):
        """클라이언트 IP 주소 추출"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def cleanup_cache(self):
        """오래된 캐시 항목 정리"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            expired_keys = []
            for key, (timestamp, count) in self.cache.items():
                if current_time - timestamp > 60:  # 1분 이상 된 항목
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            self.last_cleanup = current_time
    
    def process_request(self, request):
        """Rate limit 체크"""
        # 정기적으로 캐시 정리
        self.cleanup_cache()
        
        # Rate limit 적용 경로
        if request.path.startswith('/api/users/login/'):
            ip = self.get_client_ip(request)
            current_time = time.time()
            
            # IP별 요청 횟수 체크
            cache_key = f"rate_limit:{ip}:{request.path}"
            
            if cache_key in self.cache:
                timestamp, count = self.cache[cache_key]
                
                # 1분 이내의 요청인 경우
                if current_time - timestamp < 60:
                    if count >= 5:  # 분당 5회 제한
                        return JsonResponse({
                            'success': False,
                            'error': {
                                'message': 'Too many requests. Please try again later.',
                                'type': 'RateLimitError'
                            }
                        }, status=429)
                    
                    # 카운트 증가
                    self.cache[cache_key] = (timestamp, count + 1)
                else:
                    # 새로운 시간 윈도우 시작
                    self.cache[cache_key] = (current_time, 1)
            else:
                # 첫 요청
                self.cache[cache_key] = (current_time, 1)
        
        return None

class LoggingMiddleware(MiddlewareMixin):
    """향상된 로깅 미들웨어 (Rate limit 문제 해결)"""
    
    def process_request(self, request):
        """요청 로깅 (중요한 것만)"""
        if settings.DEBUG or request.path.startswith('/api/'):
            # 로그 레벨을 INFO로 낮춤 (ERROR만 로깅)
            if request.method in ['POST', 'PUT', 'DELETE']:
                logger.info(f"API Request: {request.method} {request.path}")
    
    def process_exception(self, request, exception):
        """예외만 ERROR 레벨로 로깅"""
        logger.error(
            f"Exception in {request.method} {request.path}: {exception}",
            exc_info=False  # 스택 트레이스 최소화
        )