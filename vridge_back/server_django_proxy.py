#!/usr/bin/env python3
"""
Django 통합 프록시 서버
헬스체크는 즉시 응답하고, API 요청은 Django로 프록시
"""
import os
import sys
import subprocess
import threading
import time
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import http.client

# Django 상태
django_port = int(os.environ.get('DJANGO_PORT', '8001'))
django_starting = True

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def do_OPTIONS(self):
        # CORS preflight 처리
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def handle_request(self):
        global django_starting
        
        # 헬스체크 경로는 즉시 응답
        if self.path in ['/', '/health', '/healthz']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        # /ready 경로는 Django 상태 확인
        if self.path == '/ready':
            if check_django():
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Django Ready')
            else:
                self.send_response(503)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Django Starting...')
            return
        
        # API 요청은 Django로 프록시
        if self.path.startswith('/api/'):
            if not check_django():
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Service starting, please wait..."}')
                return
            
            try:
                # Django로 프록시
                self.proxy_to_django()
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}"}}'.encode())
            return
        
        # 그 외 경로는 404
        self.send_response(404)
        self.end_headers()
    
    def proxy_to_django(self):
        """Django로 요청 프록시"""
        # 요청 본문 읽기
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else None
        
        # Django에 연결
        conn = http.client.HTTPConnection('127.0.0.1', django_port)
        
        # 헤더 복사
        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ['host']:
                headers[key] = value
        
        # 요청 전송
        conn.request(self.command, self.path, body, headers)
        
        # 응답 받기
        response = conn.getresponse()
        
        # 응답 상태 전송
        self.send_response(response.status)
        
        # 응답 헤더 전송
        for key, value in response.getheaders():
            if key.lower() not in ['connection']:
                self.send_header(key, value)
        self.end_headers()
        
        # 응답 본문 전송
        self.wfile.write(response.read())
        
        conn.close()
    
    def log_message(self, format, *args):
        # 헬스체크 로그는 숨김
        if '/' not in format % args or '/api/' in format % args:
            print(f"[PROXY] {format % args}")

def check_django():
    """Django 서버 확인"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(('127.0.0.1', django_port))
        sock.close()
        return result == 0
    except:
        return False

def start_django():
    """Django 시작"""
    global django_starting
    
    print("[DJANGO] Preparing Django...")
    time.sleep(2)
    
    # 환경 변수 설정
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
    
    # 마이그레이션
    print("[DJANGO] Running migrations...")
    try:
        subprocess.run(
            [sys.executable, 'manage.py', 'migrate', '--noinput'],
            capture_output=True,
            timeout=30,
            check=False
        )
    except:
        pass
    
    # Gunicorn 시작
    print(f"[DJANGO] Starting Gunicorn on port {django_port}...")
    cmd = [
        'gunicorn',
        'config.wsgi:application',
        f'--bind=127.0.0.1:{django_port}',
        '--workers=2',
        '--threads=2',
        '--timeout=120',
        '--log-level=info'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"[DJANGO] Failed: {e}")
        django_starting = False

def main():
    # 포트 설정
    proxy_port = int(os.environ.get('PORT', '8000'))
    
    print("="*60)
    print("VideoPlanet Backend with Django Integration")
    print(f"Proxy port: {proxy_port} (Railway)")
    print(f"Django port: {django_port} (Internal)")
    print("="*60)
    
    # Django를 백그라운드에서 시작
    django_thread = threading.Thread(target=start_django, daemon=True)
    django_thread.start()
    
    # 프록시 서버 시작
    print(f"[PROXY] Starting proxy server on port {proxy_port}")
    server = HTTPServer(('', proxy_port), ProxyHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()