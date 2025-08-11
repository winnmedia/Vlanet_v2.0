#!/usr/bin/env python3
"""
Railway   
Django    
"""
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

#  
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VlanetHandler(BaseHTTPRequestHandler):
    """Vlanet API  """
    
    def log_message(self, format, *args):
        """  """
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_OPTIONS(self):
        """CORS preflight """
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """GET  """
        self.handle_request('GET')
    
    def do_POST(self):
        """POST  """
        self.handle_request('POST')
    
    def send_cors_headers(self):
        """CORS  """
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Allow-Credentials', 'true')
    
    def send_json_response(self, data, status_code=200):
        """JSON  """
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_cors_headers()
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def handle_request(self, method):
        """   """
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        logger.info(f"{method} {path} - {self.address_string()}")
        
        #  
        if path in ['/', '/health/', '/api/health/']:
            self.handle_health_check()
        
        #  
        elif path == '/debug/':
            self.handle_debug()
        
        #  API
        elif path in ['/api/projects/', '/api/projects/project_list/']:
            self.handle_projects()
        
        #  API
        elif path.startswith('/api/users/notifications'):
            self.handle_notifications()
        
        #  API
        elif 'invitations' in path:
            self.handle_invitations()
        
        #  API
        elif path.startswith('/api/users/'):
            self.handle_users()
        
        #  API
        elif path.startswith('/api/'):
            self.handle_generic_api(path, method)
        
        # 404
        else:
            self.handle_not_found()
    
    def handle_health_check(self):
        """ """
        data = {
            "status": "ok",
            "service": "vlanet-standalone",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "railway_environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
            "message": "Standalone server running successfully"
        }
        self.send_json_response(data)
    
    def handle_debug(self):
        """ """
        data = {
            "server_info": {
                "type": "standalone_python_server",
                "port": os.environ.get('PORT', '8000'),
                "pid": os.getpid(),
            },
            "environment_variables": {
                "RAILWAY_ENVIRONMENT": os.environ.get('RAILWAY_ENVIRONMENT'),
                "DATABASE_URL": "Present" if os.environ.get('DATABASE_URL') else "Not set",
                "SECRET_KEY": "Present" if os.environ.get('SECRET_KEY') else "Not set",
                "PORT": os.environ.get('PORT'),
            },
            "request_info": {
                "client_address": self.address_string(),
                "server_version": self.version_string(),
            },
            "django_status": "Not loaded (standalone server mode)"
        }
        self.send_json_response(data)
    
    def handle_projects(self):
        """  API"""
        data = {
            "results": [],
            "count": 0,
            "message": "standalone :     ",
            "standalone_mode": True,
            "instructions": "Django     "
        }
        self.send_json_response(data)
    
    def handle_notifications(self):
        """ API"""
        data = {
            "results": [],
            "count": 0,
            "message": "standalone :     ",
            "standalone_mode": True
        }
        self.send_json_response(data)
    
    def handle_invitations(self):
        """ API"""
        data = {
            "results": [],
            "message": "standalone :     ",
            "standalone_mode": True
        }
        self.send_json_response(data)
    
    def handle_users(self):
        """ API"""
        data = {
            "id": 0,
            "email": "standalone@mode.com",
            "nickname": "standalone",
            "profile_image": None,
            "message": "standalone :     ",
            "standalone_mode": True
        }
        self.send_json_response(data)
    
    def handle_generic_api(self, path, method):
        """ API """
        data = {
            "message": "standalone :  API    ",
            "path": path,
            "method": method,
            "standalone_mode": True,
            "status": "service_unavailable"
        }
        self.send_json_response(data, 503)
    
    def handle_not_found(self):
        """404 """
        data = {
            "error": "Not Found",
            "message": f"Path '{self.path}' not found in standalone server",
            "available_endpoints": [
                "/health/", "/api/health/", "/debug/",
                "/api/projects/", "/api/users/notifications/",
                "/api/projects/invitations/"
            ]
        }
        self.send_json_response(data, 404)

def run_server():
    """ """
    port = int(os.environ.get('PORT', 8000))
    
    logger.info("=" * 50)
    logger.info(" Vlanet Standalone Server Starting")
    logger.info(f"Port: {port}")
    logger.info(f"Railway Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')}")
    logger.info(f"Process ID: {os.getpid()}")
    logger.info("=" * 50)
    
    server = HTTPServer(('0.0.0.0', port), VlanetHandler)
    
    logger.info(f" Server ready on http://0.0.0.0:{port}")
    logger.info("Available endpoints:")
    logger.info("  - GET /health/ ()")
    logger.info("  - GET /api/health/ (API )")
    logger.info("  - GET /debug/ ( )")
    logger.info("  - GET /api/projects/ ( )")
    logger.info("  - GET /api/users/notifications/ ()")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info(" Server stopped by user")
    except Exception as e:
        logger.error(f" Server error: {e}")
        raise
    finally:
        server.server_close()
        logger.info(" Server closed")

if __name__ == '__main__':
    run_server()