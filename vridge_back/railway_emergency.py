#!/usr/bin/env python3
"""
Railway 긴급 헬스체크 서버
Gunicorn 대신 직접 실행
"""
import os
import sys
import logging

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Django 초기화
    import django
    django.setup()
    logger.info("Django 설정 로드 성공")
    
    # WSGI 애플리케이션 가져오기
    from config.wsgi import application
    logger.info("WSGI 애플리케이션 로드 성공")
    
    # 간단한 HTTP 서버 시작
    from wsgiref.simple_server import make_server
    
    port = int(os.environ.get('PORT', 8000))
    
    logger.info(f"서버 시작 - 포트 {port}")
    
    with make_server('0.0.0.0', port, application) as httpd:
        logger.info(f"Railway 긴급 서버 실행 중 - http://0.0.0.0:{port}")
        httpd.serve_forever()
        
except Exception as e:
    logger.error(f"서버 시작 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)