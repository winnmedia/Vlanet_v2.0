#!/usr/bin/env python3
"""
가장 기본적인 Python HTTP 서버
Gunicorn 없이 직접 실행
"""
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """모든 GET 요청에 대해 헬스체크 응답"""
        # 헬스체크 경로
        if self.path in ['/', '/health', '/health/', '/api/health', '/api/health/']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'service': 'videoplanet-backend'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            # Django로 전달 시도 (옵션)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
    
    def do_HEAD(self):
        """HEAD 요청 처리"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
    
    def do_OPTIONS(self):
        """OPTIONS 요청 처리"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        """로그 출력 간소화"""
        return

def run_server():
    """서버 실행"""
    port = int(os.environ.get('PORT', 8000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthHandler)
    print(f"Health check server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()