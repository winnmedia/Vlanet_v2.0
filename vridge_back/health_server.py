#!/usr/bin/env python3
"""
독립적인 헬스체크 서버
Railway 헬스체크를 위한 경량 HTTP 서버
Django 앱과 독립적으로 실행되어 즉시 응답
"""
import os
import sys
import time
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import psutil
import json

class HealthCheckHandler(BaseHTTPRequestHandler):
    """헬스체크 요청 처리"""
    
    def log_message(self, format, *args):
        """로그 출력 커스터마이징"""
        sys.stdout.write(f"[HEALTH] {format % args}\n")
        sys.stdout.flush()
    
    def do_GET(self):
        """GET 요청 처리"""
        if self.path in ['/', '/health', '/healthz']:
            # 즉시 성공 응답
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/ready':
            # Django 앱 준비 상태 확인
            if check_django_ready():
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'ready',
                    'django': 'running',
                    'timestamp': int(time.time())
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'starting',
                    'django': 'not_ready',
                    'timestamp': int(time.time())
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_HEAD(self):
        """HEAD 요청 처리"""
        self.do_GET()
    
    def do_OPTIONS(self):
        """OPTIONS 요청 처리 (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.end_headers()

def check_django_ready():
    """Django 앱이 준비되었는지 확인"""
    django_port = int(os.environ.get('PORT', 8000))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', django_port))
        sock.close()
        return result == 0
    except:
        return False

def run_health_server(port=8001):
    """헬스체크 서버 실행"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"[HEALTH] Health check server running on port {port}")
    sys.stdout.flush()
    httpd.serve_forever()

if __name__ == '__main__':
    # Railway에서 헬스체크 포트 설정 가능
    health_port = int(os.environ.get('HEALTH_PORT', 8001))
    
    # 헬스체크 서버 시작
    print(f"[HEALTH] Starting independent health check server...")
    run_health_server(health_port)