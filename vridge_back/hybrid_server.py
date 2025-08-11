#!/usr/bin/env python3
"""
단계적 Django 복구 서버
헬스체크는 항상 작동하고, Django는 가능한 경우에만 실행
"""
import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Django 로드 시도
DJANGO_READY = False
django_error = None

def try_django_setup():
    """Django 설정 시도"""
    global DJANGO_READY, django_error
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
        
        # 로깅 비활성화
        import logging
        logging.disable(logging.CRITICAL)
        
        import django
        django.setup()
        
        # 데이터베이스 연결 테스트
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        DJANGO_READY = True
        print("✅ Django is ready")
        return True
    except Exception as e:
        django_error = str(e)
        print(f"⚠️ Django not ready: {e}")
        return False

class HybridHandler(BaseHTTPRequestHandler):
    """Django와 독립 서버를 결합한 핸들러"""
    
    def do_GET(self):
        """GET 요청 처리"""
        # 헬스체크는 항상 응답
        if self.path in ['/api/health/', '/health/', '/', '/api/health']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'ok',
                'django_ready': DJANGO_READY,
                'message': 'Server is running'
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Django가 준비되면 Django 라우팅 사용
        if DJANGO_READY and self.path.startswith('/api/'):
            self.handle_django_request()
        else:
            self.send_error(503, "Service temporarily unavailable")
    
    def do_POST(self):
        """POST 요청 처리"""
        if self.path == '/api/users/login/' and DJANGO_READY:
            self.handle_django_request()
        elif self.path == '/api/users/login/':
            # Django 없이 임시 응답
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'success': False,
                'error': 'Login service is being restored',
                'django_ready': DJANGO_READY
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.do_GET()
    
    def do_OPTIONS(self):
        """OPTIONS 요청 처리 (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def handle_django_request(self):
        """Django 요청 처리"""
        try:
            from django.core.handlers.wsgi import WSGIHandler
            from io import BytesIO
            
            # WSGI 환경 설정
            environ = {
                'REQUEST_METHOD': self.command,
                'PATH_INFO': self.path,
                'SERVER_NAME': 'localhost',
                'SERVER_PORT': str(self.server.server_port),
                'wsgi.input': BytesIO(self.rfile.read(int(self.headers.get('Content-Length', 0)))),
                'wsgi.errors': sys.stderr,
                'wsgi.url_scheme': 'http',
                'wsgi.multithread': False,
                'wsgi.multiprocess': True,
                'wsgi.run_once': False,
            }
            
            # Django 핸들러 실행
            handler = WSGIHandler()
            response = handler(environ, self.start_response)
            
            # 응답 전송
            for data in response:
                self.wfile.write(data)
        except Exception as e:
            self.send_error(500, f"Django error: {e}")
    
    def start_response(self, status, headers):
        """WSGI start_response"""
        status_code = int(status.split()[0])
        self.send_response(status_code)
        for header, value in headers:
            self.send_header(header, value)
        self.end_headers()
    
    def log_message(self, format, *args):
        """로그 비활성화"""
        pass

def django_retry_thread():
    """Django를 주기적으로 재시도하는 스레드"""
    while not DJANGO_READY:
        time.sleep(30)  # 30초마다 재시도
        print("🔄 Retrying Django setup...")
        try_django_setup()

def main():
    """메인 서버 실행"""
    port = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Starting hybrid server on port {port}")
    print("📍 Health check always available at /api/health/")
    
    # Django 설정 시도 (백그라운드)
    django_thread = threading.Thread(target=try_django_setup, daemon=True)
    django_thread.start()
    
    # Django 재시도 스레드
    retry_thread = threading.Thread(target=django_retry_thread, daemon=True)
    retry_thread.start()
    
    # HTTP 서버 시작
    server = HTTPServer(('0.0.0.0', port), HybridHandler)
    print(f"✅ Server ready at http://0.0.0.0:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == '__main__':
    main()