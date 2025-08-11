#!/usr/bin/env python3
"""
Django 복구 서버
단계별로 Django 기능을 활성화
"""

import os
import sys
import json
import time
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_minimal')
os.environ.setdefault('PYTHONUNBUFFERED', '1')

# 상태 추적
STATUS = {
    'server': 'starting',
    'django': 'not_loaded',
    'database': 'not_connected',
    'migrations': 'not_checked',
    'login_api': 'not_available',
    'errors': []
}

def try_django_setup():
    """Django 설정 시도"""
    print("🔄 Attempting Django setup...")
    
    try:
        # 1. Django import
        import django
        STATUS['django'] = 'imported'
        print("✅ Django imported")
        
        # 2. Django setup
        django.setup()
        STATUS['django'] = 'setup_complete'
        print("✅ Django setup complete")
        
        # 3. Database 연결 테스트
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                STATUS['database'] = 'connected'
                print("✅ Database connected")
        except Exception as e:
            STATUS['database'] = f'error: {str(e)[:50]}'
            print(f"⚠️ Database error: {e}")
            # 데이터베이스 없어도 계속
        
        # 4. 기본 URL 설정
        from django.urls import path
        from django.http import JsonResponse
        
        def health_view(request):
            return JsonResponse({
                'status': 'ok',
                'django': True,
                'details': STATUS
            })
        
        # URL 패턴 덮어쓰기
        from config import urls
        urls.urlpatterns = [
            path('api/health/', health_view),
            path('health/', health_view),
            path('', health_view),
        ]
        
        STATUS['django'] = 'ready'
        print("✅ Django is ready!")
        return True
        
    except Exception as e:
        STATUS['django'] = f'error: {str(e)[:50]}'
        STATUS['errors'].append({
            'time': time.time(),
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        print(f"❌ Django setup failed: {e}")
        return False

def run_django_server():
    """Django 서버 실행 시도"""
    if STATUS['django'] == 'ready':
        try:
            from django.core.management import execute_from_command_line
            port = os.environ.get('PORT', '8000')
            
            print(f"🚀 Starting Django server on port {port}")
            sys.argv = ['manage.py', 'runserver', f'0.0.0.0:{port}', '--noreload']
            execute_from_command_line(sys.argv)
        except Exception as e:
            print(f"❌ Django server failed: {e}")
            STATUS['django'] = f'server_error: {str(e)[:50]}'

class RecoveryHandler(BaseHTTPRequestHandler):
    """복구 모드 핸들러"""
    
    def do_GET(self):
        """GET 요청 처리"""
        if self.path in ['/api/health/', '/health/', '/', '/api/health']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'ok',
                'mode': 'recovery',
                'django_status': STATUS['django'],
                'database_status': STATUS['database'],
                'timestamp': time.time(),
                'details': STATUS
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """POST 요청 처리"""
        if self.path == '/api/users/login/':
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': False,
                'error': 'Login service is being restored',
                'status': STATUS
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.do_GET()
    
    def do_OPTIONS(self):
        """OPTIONS 요청 처리"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        """로그 출력"""
        # 중요한 요청만 로그
        if '/health' not in self.path:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_fallback_server():
    """폴백 HTTP 서버"""
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), RecoveryHandler)
    
    print(f"🔧 Recovery server running on port {port}")
    print(f"📍 Health check: http://0.0.0.0:{port}/api/health/")
    
    STATUS['server'] = 'running'
    server.serve_forever()

def main():
    """메인 실행"""
    print("=" * 60)
    print("🚑 Django Recovery Mode")
    print("=" * 60)
    
    # Django 설정 시도
    django_ready = try_django_setup()
    
    if django_ready and STATUS.get('database') == 'connected':
        # Django가 완전히 준비되면 Django 서버 실행
        print("✅ Starting full Django server")
        run_django_server()
    else:
        # Django가 준비되지 않으면 폴백 서버
        print("⚠️ Starting fallback server")
        
        # Django 재시도 스레드
        def retry_django():
            while STATUS['django'] != 'ready':
                time.sleep(30)
                print("🔄 Retrying Django setup...")
                if try_django_setup():
                    print("✅ Django recovered! Restart server to use Django.")
        
        retry_thread = Thread(target=retry_django, daemon=True)
        retry_thread.start()
        
        # 폴백 서버 실행
        run_fallback_server()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        
        # 최후의 수단 - 단순 HTTP 서버
        print("🆘 Starting emergency server")
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class EmergencyHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK - Emergency mode')
            def log_message(self, *args): pass
        
        port = int(os.environ.get('PORT', 8000))
        HTTPServer(('0.0.0.0', port), EmergencyHandler).serve_forever()