#!/usr/bin/env python3
"""
Railway 전용 극초경량 헬스체크 WSGI 앱
제로 의존성, 즉시 응답
"""

def application(environ, start_response):
    """
    모든 헬스체크 경로에 대해 무조건 200 OK 반환
    Railway가 체크하는 /health/ 경로에 즉시 응답
    """
    path = environ.get('PATH_INFO', '/')
    
    # 헬스체크 경로들 - Railway는 /health/를 체크
    if path in ['/', '/health/', '/health', '/api/health/', '/api/health']:
        # 무조건 성공
        response = b'{"status":"healthy","service":"videoplanet"}'
        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response))),
            ('Cache-Control', 'no-cache'),
        ]
        start_response(status, headers)
        return [response]
    
    # 다른 경로는 404
    response = b'{"error":"Not Found"}'
    status = '404 Not Found'
    headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response))),
    ]
    start_response(status, headers)
    return [response]