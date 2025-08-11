#!/usr/bin/env python3
"""
헬스체크 서버와 Django 앱을 함께 실행
헬스체크는 즉시 응답, Django는 백그라운드에서 시작
"""
import os
import sys
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Django 준비 상태
django_ready = False
django_error = None

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global django_ready, django_error
        
        # 루트 경로는 항상 OK (Railway 헬스체크)
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        # /status 경로는 Django 상태 확인
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            status = f"Django: {'Ready' if django_ready else 'Starting...'}"
            if django_error:
                status += f"\nError: {django_error}"
            self.wfile.write(status.encode())
            return
        
        # 다른 경로는 404
        self.send_response(404)
        self.end_headers()
    
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # 헬스체크 로그는 최소화
        if '/status' not in format % args:
            return

def run_health_server(port):
    """헬스체크 서버 실행"""
    print(f"[HEALTH] Starting health check server on port {port}")
    server = HTTPServer(('', port), HealthHandler)
    server.serve_forever()

def run_django():
    """Django 앱 실행"""
    global django_ready, django_error
    
    print("[DJANGO] Starting Django setup...")
    
    # 환경 변수 설정
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
    
    # 1. 마이그레이션 실행 (실패해도 계속)
    print("[DJANGO] Running migrations...")
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'migrate', '--noinput'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("[DJANGO] Migrations completed")
        else:
            print(f"[DJANGO] Migration warning: {result.stderr[:200]}")
    except Exception as e:
        print(f"[DJANGO] Migration skipped: {e}")
    
    # 2. 정적 파일 수집 (선택적)
    if os.environ.get('COLLECT_STATIC') != 'false':
        print("[DJANGO] Collecting static files...")
        try:
            subprocess.run(
                [sys.executable, 'manage.py', 'collectstatic', '--noinput'],
                capture_output=True,
                timeout=10
            )
            print("[DJANGO] Static files collected")
        except:
            print("[DJANGO] Static files skipped")
    
    # 3. Django 서버 시작
    print("[DJANGO] Starting Gunicorn...")
    django_port = int(os.environ.get('DJANGO_PORT', '8001'))
    
    try:
        # Gunicorn 실행
        cmd = [
            'gunicorn',
            'config.wsgi:application',
            f'--bind=127.0.0.1:{django_port}',
            '--workers=1',
            '--threads=2',
            '--timeout=120',
            '--log-level=info',
            '--access-logfile=-',
            '--error-logfile=-'
        ]
        
        print(f"[DJANGO] Command: {' '.join(cmd)}")
        django_ready = True
        
        # Gunicorn 실행 (블로킹)
        subprocess.run(cmd, check=True)
        
    except Exception as e:
        django_error = str(e)
        print(f"[DJANGO] Error: {django_error}")

def main():
    """메인 실행 함수"""
    # 포트 설정
    health_port = int(os.environ.get('PORT', '8000'))
    
    print("="*50)
    print("VideoPlanet Backend Starting")
    print(f"Health check port: {health_port}")
    print(f"Django port: {os.environ.get('DJANGO_PORT', '8001')}")
    print("="*50)
    
    # Django를 백그라운드 스레드에서 실행
    django_thread = threading.Thread(target=run_django, daemon=True)
    django_thread.start()
    
    # 헬스체크 서버 실행 (메인 스레드)
    run_health_server(health_port)

if __name__ == '__main__':
    main()