#!/usr/bin/env python3
"""
Railway Ultimate Simple Health Check Server
Django 의존성 완전 제거, Python 표준 라이브러리만 사용
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


class HealthHandler(BaseHTTPRequestHandler):
    """초단순 헬스체크 핸들러"""
    
    def do_GET(self):
        """모든 GET 요청을 200 OK로 응답"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 건강 상태 응답
        response = {
            "status": "healthy",
            "service": "videoplanet-backend",
            "path": self.path,
            "method": "GET"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print(f"[HEALTH] {self.command} {self.path} -> 200 OK", flush=True)
    
    def do_POST(self):
        """POST 요청도 200 OK로 응답"""
        self.do_GET()
    
    def do_HEAD(self):
        """HEAD 요청 처리"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        print(f"[HEALTH] {self.command} {self.path} -> 200 OK", flush=True)
    
    def log_message(self, format, *args):
        """로그 메시지 출력"""
        print(f"[HEALTH] {format % args}", flush=True)


def run_server():
    """헬스체크 서버 실행"""
    port = int(os.environ.get('PORT', 8000))
    
    print(f"[HEALTH] Starting health server on port {port}", flush=True)
    print(f"[HEALTH] Working directory: {os.getcwd()}", flush=True)
    print(f"[HEALTH] Environment PORT: {os.environ.get('PORT', 'not set')}", flush=True)
    
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    
    print(f"[HEALTH] Server ready at http://0.0.0.0:{port}/", flush=True)
    print(f"[HEALTH] Health check endpoint: http://0.0.0.0:{port}/health/", flush=True)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[HEALTH] Server stopping...", flush=True)
        server.server_close()


if __name__ == '__main__':
    run_server()