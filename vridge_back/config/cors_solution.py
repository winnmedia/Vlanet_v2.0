"""
Railway 환경에서 작동하는 강력한 CORS 솔루션
이 미들웨어는 django-cors-headers와 독립적으로 작동하여 CORS를 보장합니다.
"""
import logging
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RailwayCORSMiddleware(MiddlewareMixin):
    """
    Railway 환경에 최적화된 CORS 미들웨어
    django-cors-headers가 실패하더라도 CORS를 보장합니다.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # 허용된 origin 목록
        self.allowed_origins = [
            'https://vlanet.net',
            'https://www.vlanet.net',
            'https://videoplanet-seven.vercel.app',
            'http://localhost:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:3001',
        ]
        
        # 허용된 메서드
        self.allowed_methods = [
            'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD'
        ]
        
        # 허용된 헤더
        self.allowed_headers = [
            'accept',
            'accept-encoding',
            'authorization',
            'content-type',
            'dnt',
            'origin',
            'user-agent',
            'x-csrftoken',
            'x-requested-with',
            'cache-control',
            'pragma',
            'x-idempotency-key',
        ]
        
        # 노출할 헤더
        self.expose_headers = [
            'Content-Type',
            'X-CSRFToken',
            'Content-Length',
        ]
    
    def process_request(self, request):
        """OPTIONS 요청을 즉시 처리"""
        if request.method == 'OPTIONS':
            logger.info(f"Handling OPTIONS request for {request.path}")
            response = HttpResponse()
            response['Content-Length'] = '0'
            response.status_code = 204
            return self._add_cors_headers(request, response)
        return None
    
    def process_response(self, request, response):
        """모든 응답에 CORS 헤더 추가"""
        return self._add_cors_headers(request, response)
    
    def _add_cors_headers(self, request, response):
        """CORS 헤더를 응답에 추가"""
        origin = request.META.get('HTTP_ORIGIN', '')
        
        # Origin 검증 및 설정
        if origin:
            # 개발 환경이거나 허용된 origin인 경우
            if self._is_allowed_origin(origin):
                response['Access-Control-Allow-Origin'] = origin
                response['Vary'] = 'Origin'
            else:
                # 프로덕션에서도 일단 허용 (디버깅 목적)
                logger.warning(f"Allowing unregistered origin: {origin}")
                response['Access-Control-Allow-Origin'] = origin
                response['Vary'] = 'Origin'
        else:
            # Origin 헤더가 없는 경우 (same-origin 요청 등)
            # 이 경우 CORS 헤더를 추가하지 않음
            pass
        
        # Origin이 있고 허용된 경우에만 나머지 헤더 추가
        if 'Access-Control-Allow-Origin' in response:
            # Credentials 허용
            response['Access-Control-Allow-Credentials'] = 'true'
            
            # OPTIONS 요청에 대한 추가 헤더
            if request.method == 'OPTIONS':
                response['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
                response['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
                response['Access-Control-Max-Age'] = '86400'  # 24시간
            
            # 모든 요청에 대해 Expose Headers 추가
            response['Access-Control-Expose-Headers'] = ', '.join(self.expose_headers)
        
        # 디버깅 로그
        if origin:
            logger.debug(
                f"CORS headers added - Method: {request.method}, "
                f"Path: {request.path}, Origin: {origin}, "
                f"Allow-Origin: {response.get('Access-Control-Allow-Origin', 'Not set')}"
            )
        
        return response
    
    def _is_allowed_origin(self, origin):
        """Origin이 허용된 목록에 있는지 확인"""
        # 정확한 매칭
        if origin in self.allowed_origins:
            return True
        
        # Vercel 프리뷰 배포 허용
        if '.vercel.app' in origin and origin.startswith('https://'):
            return True
        
        # Railway 앱 허용
        if '.railway.app' in origin and origin.startswith('https://'):
            return True
        
        return False


class OptionsHandlerMiddleware(MiddlewareMixin):
    """
    OPTIONS 요청을 최우선으로 처리하는 미들웨어
    다른 모든 미들웨어보다 먼저 실행되어야 함
    """
    
    def process_request(self, request):
        """OPTIONS 요청만 처리"""
        if request.method == 'OPTIONS':
            logger.info(f"Fast OPTIONS handling for {request.path}")
            response = HttpResponse()
            response.status_code = 204
            response['Content-Length'] = '0'
            
            # 기본 CORS 헤더 설정
            origin = request.META.get('HTTP_ORIGIN', '*')
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
            response['Access-Control-Allow-Headers'] = (
                'accept, accept-encoding, authorization, content-type, dnt, '
                'origin, user-agent, x-csrftoken, x-requested-with, '
                'cache-control, pragma, x-idempotency-key'
            )
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = '86400'
            response['Vary'] = 'Origin'
            
            return response
        
        return None