#!/usr/bin/env python3
"""
극도로 단순한 헬스체크 전용 WSGI 앱
Django 관련 코드 완전 제거
"""

def application(environ, start_response):
    """무조건 200 OK 반환"""
    
    # 응답 본문
    response = b'{"status":"healthy","service":"videoplanet"}'
    
    # 헤더 설정
    status = '200 OK'
    headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response))),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
    ]
    
    # 응답 반환
    start_response(status, headers)
    return [response]