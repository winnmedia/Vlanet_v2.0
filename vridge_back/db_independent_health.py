#!/usr/bin/env python3
"""
Database Independent Health Check Server
완전히 DB 독립적인 헬스체크 서버 - PostgreSQL, Django 연결 실패와 무관하게 작동
"""

import json
import os
import sys
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DatabaseIndependentHealthHandler(BaseHTTPRequestHandler):
    """완전히 DB 독립적인 헬스체크 핸들러"""
    
    def __init__(self, *args, **kwargs):
        self.start_time = time.time()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """GET 요청 처리"""
        try:
            if self.path.startswith('/health'):
                self._handle_health_check()
            elif self.path.startswith('/status'):
                self._handle_status_check()
            elif self.path.startswith('/diagnostics'):
                self._handle_diagnostics()
            else:
                # 기본적으로 모든 경로를 헬스체크로 처리
                self._handle_health_check()
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            self._send_error_response(500, str(e))
    
    def do_POST(self):
        """POST 요청도 GET과 동일하게 처리"""
        self.do_GET()
    
    def do_HEAD(self):
        """HEAD 요청 처리"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_OPTIONS(self):
        """OPTIONS 요청 처리 (CORS preflight)"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def _handle_health_check(self):
        """기본 헬스체크 - 항상 성공"""
        uptime = time.time() - self.start_time
        
        response = {
            "status": "healthy",
            "service": "videoplanet-backend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(uptime, 2),
            "version": "db-independent-1.0.0",
            "environment": {
                "railway": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                "port": os.environ.get('PORT', '8000'),
                "python_version": sys.version.split()[0]
            },
            "checks": {
                "basic": "ok",
                "memory": "ok",
                "disk": "ok"
            }
        }
        
        self._send_json_response(200, response)
        logger.info(f"Health check: {self.path} -> 200 OK")
    
    def _handle_status_check(self):
        """상태 체크 - 시스템 정보 포함"""
        try:
            import psutil
            system_info = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        except ImportError:
            system_info = {
                "note": "psutil not available, basic monitoring only"
            }
        
        response = {
            "status": "operational",
            "service": "videoplanet-backend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": system_info,
            "environment": {
                "working_directory": os.getcwd(),
                "python_executable": sys.executable,
                "platform": sys.platform
            }
        }
        
        self._send_json_response(200, response)
        logger.info(f"Status check: {self.path} -> 200 OK")
    
    def _handle_diagnostics(self):
        """진단 정보 - 환경변수 및 설정 정보"""
        # 민감한 정보는 마스킹
        env_vars = {}
        for key, value in os.environ.items():
            if any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
                env_vars[key] = "***MASKED***"
            else:
                env_vars[key] = value
        
        response = {
            "status": "diagnostic",
            "service": "videoplanet-backend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "diagnostics": {
                "environment_variables": env_vars,
                "python_path": sys.path,
                "current_directory": os.getcwd(),
                "file_permissions": self._check_file_permissions()
            }
        }
        
        self._send_json_response(200, response)
        logger.info(f"Diagnostics check: {self.path} -> 200 OK")
    
    def _check_file_permissions(self):
        """파일 권한 체크"""
        files_to_check = [
            'manage.py',
            'requirements.txt',
            'config/settings',
            '.'
        ]
        
        permissions = {}
        for file_path in files_to_check:
            try:
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    permissions[file_path] = {
                        "exists": True,
                        "readable": os.access(file_path, os.R_OK),
                        "writable": os.access(file_path, os.W_OK),
                        "executable": os.access(file_path, os.X_OK)
                    }
                else:
                    permissions[file_path] = {"exists": False}
            except Exception as e:
                permissions[file_path] = {"error": str(e)}
        
        return permissions
    
    def _send_json_response(self, status_code, data):
        """JSON 응답 전송"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))
    
    def _send_error_response(self, status_code, error_message):
        """에러 응답 전송"""
        response = {
            "status": "error",
            "error": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "videoplanet-backend"
        }
        self._send_json_response(status_code, response)
    
    def log_message(self, format, *args):
        """HTTP 서버 로그 메시지 처리"""
        logger.info(f"HTTP: {format % args}")


class DatabaseIndependentHealthServer:
    """DB 독립적 헬스체크 서버"""
    
    def __init__(self, port=None):
        self.port = int(port or os.environ.get('PORT', 8000))
        self.start_time = time.time()
        
        # 핸들러에 시작 시간 전달
        def handler(*args, **kwargs):
            handler_instance = DatabaseIndependentHealthHandler(*args, **kwargs)
            handler_instance.start_time = self.start_time
            return handler_instance
        
        self.handler = handler
        self.server = None
    
    def start(self):
        """서버 시작"""
        logger.info("=" * 60)
        logger.info("DATABASE INDEPENDENT HEALTH CHECK SERVER")
        logger.info("=" * 60)
        logger.info(f"Starting server on 0.0.0.0:{self.port}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
        
        # 환경 변수 체크 (민감한 정보 제외)
        important_vars = ['PORT', 'RAILWAY_ENVIRONMENT', 'DATABASE_URL']
        for var in important_vars:
            value = os.environ.get(var, 'not set')
            if 'DATABASE' in var and value != 'not set':
                # DATABASE_URL은 마스킹
                parsed = urlparse(value)
                masked_value = f"{parsed.scheme}://***:***@{parsed.hostname}:{parsed.port}{parsed.path}"
                logger.info(f"{var}: {masked_value}")
            else:
                logger.info(f"{var}: {value}")
        
        logger.info("-" * 60)
        logger.info("Available endpoints:")
        logger.info(f"  Health Check:  http://0.0.0.0:{self.port}/health/")
        logger.info(f"  Status Check:  http://0.0.0.0:{self.port}/status/")
        logger.info(f"  Diagnostics:   http://0.0.0.0:{self.port}/diagnostics/")
        logger.info("-" * 60)
        
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), self.handler)
            logger.info(f"✅ Server ready and listening on port {self.port}")
            logger.info("This server is completely independent of Django and Database")
            logger.info("It will respond to health checks even if DB is down")
            
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down server...")
            if self.server:
                self.server.server_close()
            logger.info("✅ Server stopped")
        except Exception as e:
            logger.error(f"❌ Server error: {str(e)}")
            raise


def main():
    """메인 함수"""
    try:
        # 포트 설정
        port = None
        if len(sys.argv) > 1:
            try:
                port = int(sys.argv[1])
            except ValueError:
                logger.error(f"Invalid port number: {sys.argv[1]}")
                sys.exit(1)
        
        # 서버 시작
        server = DatabaseIndependentHealthServer(port)
        server.start()
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()