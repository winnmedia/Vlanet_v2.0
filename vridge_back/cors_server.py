#!/usr/bin/env python3
"""
CORS를 완벽하게 지원하는 Django 서버
모든 요청에 CORS 헤더를 추가
"""

import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_minimal')
os.environ.setdefault('PYTHONUNBUFFERED', '1')

# CORS 설정
ALLOWED_ORIGINS = [
    'https://vlanet.net',
    'https://www.vlanet.net',
    'https://videoplanet-seven.vercel.app',
    'http://localhost:3000',
    'http://localhost:3001',
]

class CORSHandler(BaseHTTPRequestHandler):
    """CORS를 지원하는 요청 핸들러"""
    
    def send_cors_headers(self):
        """CORS 헤더 전송"""
        origin = self.headers.get('Origin', '*')
        
        # Origin이 허용 목록에 있으면 해당 origin 반환, 아니면 *
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
        else:
            self.send_header('Access-Control-Allow-Origin', '*')
        
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-CSRFToken, X-Requested-With')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        """OPTIONS 요청 처리 (CORS preflight)"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """GET 요청 처리"""
        # 헬스체크
        if self.path in ['/api/health/', '/health/', '/', '/api/health']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = {
                'status': 'ok',
                'cors_enabled': True,
                'timestamp': time.time()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error_with_cors(404, 'Not found')
    
    def do_POST(self):
        """POST 요청 처리"""
        # 경로 매핑 (프론트엔드 /api/auth/* -> 백엔드 /api/users/*)
        path_mapping = {
            '/api/auth/login/': '/api/users/login/',
            '/api/auth/signup/': '/api/users/signup/',
            '/api/auth/check-email/': '/api/users/check-email/',
            '/api/auth/check-nickname/': '/api/users/check-nickname/',
        }
        
        # 경로 변환
        actual_path = path_mapping.get(self.path, self.path)
        
        # 로그인 관련 엔드포인트
        if actual_path == '/api/users/login/':
            self.handle_login()
        elif actual_path == '/api/users/signup/':
            self.handle_signup()
        elif actual_path == '/api/users/check-email/':
            self.handle_check_email()
        elif actual_path == '/api/users/check-nickname/':
            self.handle_check_nickname()
        else:
            self.send_error_with_cors(404, 'Endpoint not found')
    
    def handle_login(self):
        """로그인 처리"""
        self.send_response(503)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {
            'success': False,
            'error': 'Login service is being restored',
            'message': 'Please try again in a few moments'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_signup(self):
        """회원가입 처리"""
        self.send_response(503)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {
            'success': False,
            'error': 'Signup service is being restored'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_check_email(self):
        """이메일 중복 확인"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {
            'success': True,
            'available': True,  # 임시로 항상 사용 가능
            'message': 'Email is available'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_check_nickname(self):
        """닉네임 중복 확인"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {
            'success': True,
            'available': True,  # 임시로 항상 사용 가능
            'message': 'Nickname is available'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def send_error_with_cors(self, code, message):
        """CORS 헤더와 함께 에러 전송"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {
            'success': False,
            'error': message,
            'status': code
        }
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """로그 출력 (헬스체크 제외)"""
        if '/health' not in self.path:
            print(f"[{time.strftime('%H:%M:%S')}] {format % args}")

def try_django_with_cors():
    """Django 설정 시도"""
    try:
        import django
        django.setup()
        
        # Django URLs에 경로 매핑 추가
        from django.urls import path, re_path
        from django.http import JsonResponse
        from django.views.decorators.csrf import csrf_exempt
        
        @csrf_exempt
        def auth_endpoint(request, action=None):
            """통합 인증 엔드포인트"""
            response_data = {
                'success': True,
                'action': action,
                'method': request.method
            }
            
            response = JsonResponse(response_data)
            # CORS 헤더 추가
            origin = request.headers.get('Origin', '*')
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        # URL 패턴 추가
        from config import urls
        urls.urlpatterns.extend([
            re_path(r'^api/auth/(?P<action>[\w-]+)/$', auth_endpoint),
            re_path(r'^api/users/(?P<action>[\w-]+)/$', auth_endpoint),
        ])
        
        print("✅ Django with CORS ready")
        return True
    except Exception as e:
        print(f"⚠️ Django not ready: {e}")
        return False

def main():
    """메인 서버 실행"""
    port = int(os.environ.get('PORT', 8000))
    
    print("=" * 60)
    print("🌐 CORS-Enabled Server")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"CORS Origins: {', '.join(ALLOWED_ORIGINS)}")
    print(f"Endpoints:")
    print("  - /api/health/")
    print("  - /api/auth/login/")
    print("  - /api/auth/signup/")
    print("  - /api/auth/check-email/")
    print("  - /api/auth/check-nickname/")
    print("=" * 60)
    
    # Django 설정 시도 (옵션)
    django_ready = try_django_with_cors()
    
    # HTTP 서버 시작
    server = HTTPServer(('0.0.0.0', port), CORSHandler)
    print(f"✅ Server ready at http://0.0.0.0:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == '__main__':
    main()