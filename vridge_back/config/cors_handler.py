"""
긴급 CORS 핸들러 - Railway 환경에서 CORS 문제 해결
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

class EmergencyCORSMiddleware(MiddlewareMixin):
    """
    긴급 CORS 미들웨어 - corsheaders가 작동하지 않을 때 사용
    settings_base.py의 MIDDLEWARE 리스트 최상단에 추가 필요
    """
    
    def process_request(self, request):
        """OPTIONS 요청 즉시 처리"""
        if request.method == 'OPTIONS':
            response = HttpResponse()
            self._set_cors_headers(request, response)
            return response
        return None
    
    def process_response(self, request, response):
        """모든 응답에 CORS 헤더 추가"""
        self._set_cors_headers(request, response)
        return response
    
    def _set_cors_headers(self, request, response):
        """CORS 헤더 설정"""
        origin = request.META.get('HTTP_ORIGIN')
        
        # 허용된 origin 목록
        allowed_origins = [
            'https://vlanet.net',
            'https://www.vlanet.net',
            'http://localhost:3000',
            'http://localhost:3001',
        ]
        
        # 개발 환경이거나 허용된 origin인 경우
        if origin in allowed_origins or origin:  # 임시로 모든 origin 허용
            response['Access-Control-Allow-Origin'] = origin
        else:
            # origin이 없으면 wildcard 사용 (보안상 권장하지 않지만 긴급 수정)
            response['Access-Control-Allow-Origin'] = '*'
        
        # 기본 CORS 헤더
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = (
            'accept, accept-encoding, authorization, content-type, dnt, '
            'origin, user-agent, x-csrftoken, x-requested-with, cache-control, pragma'
        )
        
        # OPTIONS 요청에 대한 추가 헤더
        if request.method == 'OPTIONS':
            response['Access-Control-Max-Age'] = '86400'
            response['Content-Length'] = '0'
        
        # 디버깅 로그
        logger.info(f"CORS headers set for {request.method} {request.path} from {origin}")
        
        return response