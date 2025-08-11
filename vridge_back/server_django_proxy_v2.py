#!/usr/bin/env python3
"""
Django 통합 프록시 서버 v2
개선된 프로세스 관리와 상세한 모니터링 기능 포함
"""
import os
import sys
import subprocess
import threading
import time
import socket
import json
import signal
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import http.client
from datetime import datetime

# 전역 상태 관리
class DjangoManager:
    def __init__(self):
        self.process = None
        self.port = int(os.environ.get('DJANGO_PORT', '8001'))
        self.status = "NOT_STARTED"
        self.error = None
        self.start_time = None
        self.health_check_count = 0
        self.last_health_check = None
        self.startup_logs = []
        
    def add_log(self, message):
        """시작 로그 추가"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.startup_logs.append(log_entry)
        print(log_entry)
        
    def is_port_available(self):
        """포트가 사용 가능한지 확인"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', self.port))
            sock.close()
            return result != 0  # 연결 실패 = 포트 사용 가능
        except Exception as e:
            self.add_log(f"Port check error: {e}")
            return True
            
    def check_django_health(self):
        """Django 서버 상태 확인"""
        self.health_check_count += 1
        self.last_health_check = datetime.now()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', self.port))
            sock.close()
            
            if result == 0:
                # 실제 Django 응답 확인
                try:
                    conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=2)
                    conn.request("GET", "/api/health/")
                    response = conn.getresponse()
                    conn.close()
                    return response.status == 200
                except:
                    return False
            return False
        except Exception as e:
            self.add_log(f"Health check error: {e}")
            return False
    
    def start(self):
        """Django 서버 시작"""
        self.status = "STARTING"
        self.start_time = datetime.now()
        self.add_log("Starting Django initialization...")
        
        try:
            # 포트 확인
            if not self.is_port_available():
                self.add_log(f"Port {self.port} is already in use, attempting to kill existing process...")
                self.kill_port_process()
                time.sleep(2)
            
            # 환경 변수 설정
            env = os.environ.copy()
            env['DJANGO_SETTINGS_MODULE'] = 'config.settings.railway'
            env['PYTHONUNBUFFERED'] = '1'
            
            # 데이터베이스 연결 테스트
            self.add_log("Testing database connection...")
            db_test = subprocess.run(
                [sys.executable, 'manage.py', 'dbshell', '--command=SELECT 1;'],
                env=env,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if db_test.returncode != 0:
                self.add_log(f"Database connection failed: {db_test.stderr}")
                # 데이터베이스 실패해도 계속 진행 (SQLite fallback 가능)
            else:
                self.add_log("Database connection successful")
            
            # 마이그레이션 실행
            self.add_log("Running database migrations...")
            migrate_result = subprocess.run(
                [sys.executable, 'manage.py', 'migrate', '--noinput'],
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if migrate_result.returncode != 0:
                self.add_log(f"Migration warning: {migrate_result.stderr[:500]}")
            else:
                self.add_log("Migrations completed successfully")
            
            # Static 파일 수집 (production에서만)
            if not os.environ.get('DEBUG', 'False') == 'True':
                self.add_log("Collecting static files...")
                subprocess.run(
                    [sys.executable, 'manage.py', 'collectstatic', '--noinput'],
                    env=env,
                    capture_output=True,
                    timeout=30
                )
            
            # Gunicorn 시작
            self.add_log(f"Starting Gunicorn on port {self.port}...")
            cmd = [
                'gunicorn',
                'config.wsgi:application',
                f'--bind=127.0.0.1:{self.port}',
                '--workers=2',
                '--threads=4',
                '--timeout=120',
                '--access-logfile=-',
                '--error-logfile=-',
                '--log-level=info',
                '--capture-output',
                '--enable-stdio-inheritance'
            ]
            
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 프로세스 출력 모니터링 스레드
            def monitor_output():
                for line in self.process.stdout:
                    if line.strip():
                        self.add_log(f"[Gunicorn] {line.strip()}")
                        if "Booting worker" in line:
                            self.status = "RUNNING"
                        elif "ERROR" in line:
                            self.error = line.strip()
            
            monitor_thread = threading.Thread(target=monitor_output, daemon=True)
            monitor_thread.start()
            
            # Django 시작 대기
            self.add_log("Waiting for Django to start...")
            max_attempts = 30
            for i in range(max_attempts):
                time.sleep(2)
                if self.check_django_health():
                    self.status = "RUNNING"
                    self.add_log(f"Django started successfully after {i*2} seconds")
                    return True
                    
                if self.process.poll() is not None:
                    # 프로세스가 종료됨
                    self.status = "FAILED"
                    self.error = f"Gunicorn process exited with code {self.process.returncode}"
                    self.add_log(self.error)
                    return False
                    
            self.status = "TIMEOUT"
            self.error = "Django failed to start within 60 seconds"
            self.add_log(self.error)
            return False
            
        except Exception as e:
            self.status = "ERROR"
            self.error = str(e)
            self.add_log(f"Fatal error: {e}")
            self.add_log(traceback.format_exc())
            return False
    
    def kill_port_process(self):
        """포트를 사용 중인 프로세스 종료"""
        try:
            result = subprocess.run(
                f"lsof -ti:{self.port} | xargs kill -9",
                shell=True,
                capture_output=True
            )
            self.add_log(f"Killed process on port {self.port}")
        except:
            pass
    
    def stop(self):
        """Django 서버 중지"""
        if self.process:
            self.add_log("Stopping Django...")
            self.process.terminate()
            time.sleep(2)
            if self.process.poll() is None:
                self.process.kill()
            self.status = "STOPPED"
    
    def get_status(self):
        """상태 정보 반환"""
        uptime = None
        if self.start_time:
            uptime = str(datetime.now() - self.start_time).split('.')[0]
            
        return {
            "status": self.status,
            "port": self.port,
            "error": self.error,
            "uptime": uptime,
            "health_checks": self.health_check_count,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "is_healthy": self.check_django_health(),
            "startup_logs": self.startup_logs[-20:]  # 마지막 20개 로그
        }

# Django 매니저 인스턴스
django_manager = DjangoManager()

class ImprovedProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def handle_request(self):
        # 기본 헬스체크 - Railway 헬스체크용
        if self.path in ['/', '/health', '/healthz']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        # Django 상태 확인 엔드포인트
        if self.path == '/django-status':
            status = django_manager.get_status()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status, indent=2).encode())
            return
        
        # Django 준비 상태
        if self.path == '/ready':
            if django_manager.status == "RUNNING" and django_manager.check_django_health():
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Django Ready')
            else:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                status = django_manager.get_status()
                self.wfile.write(json.dumps({
                    "status": "not_ready",
                    "django": status
                }, indent=2).encode())
            return
        
        # API 요청 처리
        if self.path.startswith('/api/') or self.path.startswith('/admin/'):
            if django_manager.status != "RUNNING":
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                status = django_manager.get_status()
                self.wfile.write(json.dumps({
                    "error": "Service temporarily unavailable",
                    "details": status
                }, indent=2).encode())
                return
            
            try:
                self.proxy_to_django()
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Bad Gateway",
                    "details": str(e)
                }, indent=2).encode())
            return
        
        # 404 for other paths
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "Not Found",
            "path": self.path
        }).encode())
    
    def proxy_to_django(self):
        """Django로 요청 프록시"""
        # 요청 본문 읽기
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else None
        
        # Django 연결
        conn = http.client.HTTPConnection('127.0.0.1', django_manager.port, timeout=30)
        
        # 헤더 복사
        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ['host', 'connection']:
                headers[key] = value
        
        # 요청 전송
        conn.request(self.command, self.path, body, headers)
        
        # 응답 받기
        response = conn.getresponse()
        
        # 응답 전송
        self.send_response(response.status)
        for key, value in response.getheaders():
            if key.lower() not in ['connection', 'transfer-encoding']:
                self.send_header(key, value)
        self.end_headers()
        
        # 본문 전송
        self.wfile.write(response.read())
        conn.close()
    
    def log_message(self, format, *args):
        # 헬스체크 로그 필터링
        message = format % args
        if not any(path in message for path in ['/', '/health', '/healthz']) or '/api/' in message:
            print(f"[PROXY] {message}")

def signal_handler(signum, frame):
    """시그널 핸들러"""
    print(f"\nReceived signal {signum}, shutting down...")
    django_manager.stop()
    sys.exit(0)

def main():
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 포트 설정
    proxy_port = int(os.environ.get('PORT', '8000'))
    
    print("="*70)
    print("VideoPlanet Backend - Enhanced Django Integration v2")
    print(f"Proxy Port: {proxy_port} (Railway)")
    print(f"Django Port: {django_manager.port} (Internal)")
    print(f"Environment: {'DEBUG' if os.environ.get('DEBUG') == 'True' else 'PRODUCTION'}")
    print("="*70)
    
    # Django 시작
    print("\n[INIT] Starting Django server...")
    django_thread = threading.Thread(target=django_manager.start, daemon=True)
    django_thread.start()
    
    # 프록시 서버 시작
    print(f"\n[INIT] Starting proxy server on port {proxy_port}...")
    server = HTTPServer(('', proxy_port), ImprovedProxyHandler)
    
    print(f"[READY] Server is running. Check status at /django-status")
    print(f"[READY] Health check at /")
    print(f"[READY] Django readiness at /ready")
    print("-"*70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        django_manager.stop()

if __name__ == '__main__':
    main()