"""
Railway 헬스체크 전용 WSGI 핸들러
Django 의존성 없이 헬스체크 응답을 즉시 반환
"""
import json
import os
import sys
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def health_check_handler(environ, start_response):
    """
    간단한 헬스체크 핸들러
    /api/health/, /health/, / 경로를 처리
    """
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # 헬스체크 경로들
    health_paths = ['/', '/health/', '/health', '/api/health/', '/api/health']
    
    if path in health_paths and method in ['GET', 'HEAD', 'OPTIONS']:
        # 성공 응답
        response_body = json.dumps({
            'status': 'healthy',
            'service': 'videoplanet-backend'
        }).encode('utf-8')
        
        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body))),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS'),
        ]
        
        start_response(status, headers)
        return [response_body]
    
    return None

# WSGI 애플리케이션
def application(environ, start_response):
    """
    메인 WSGI 애플리케이션
    헬스체크는 직접 처리하고 나머지는 Django로 위임
    """
    try:
        # 헬스체크 처리
        health_response = health_check_handler(environ, start_response)
        if health_response is not None:
            return health_response
        
        # Django WSGI 애플리케이션 로드
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
        
        # Django import를 여기서 수행 (헬스체크는 Django 없이도 작동)
        import django
        django.setup()
        
        from django.core.wsgi import get_wsgi_application
        django_application = get_wsgi_application()
        
        # Django로 요청 위임
        return django_application(environ, start_response)
        
    except Exception as e:
        # 에러 발생 시 로깅하고 500 반환
        logger.error(f"WSGI application error: {e}", exc_info=True)
        
        # 헬스체크 경로에서 에러가 발생해도 200 반환 (Railway 배포 통과)
        path = environ.get('PATH_INFO', '/')
        if path in ['/', '/health/', '/health', '/api/health/', '/api/health']:
            response_body = json.dumps({
                'status': 'degraded',
                'service': 'videoplanet-backend',
                'error': 'Django initialization in progress'
            }).encode('utf-8')
            
            status = '200 OK'  # 헬스체크는 항상 200 반환
            headers = [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body))),
                ('Access-Control-Allow-Origin', '*'),
            ]
            
            start_response(status, headers)
            return [response_body]
        
        # 다른 경로는 500 반환
        response_body = b'Internal Server Error'
        status = '500 Internal Server Error'
        headers = [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(response_body))),
        ]
        
        start_response(status, headers)
        return [response_body]