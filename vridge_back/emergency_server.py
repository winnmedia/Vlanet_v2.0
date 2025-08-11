#!/usr/bin/env python3
"""
  - Django      
"""
import os
import json
from wsgiref.simple_server import make_server

def cors_headers(environ=None):
    """CORS  """
    #  origin 
    allowed_origins = [
        'https://vlanet.net',
        'https://www.vlanet.net',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
    
    # Request Origin  
    origin = None
    if environ:
        origin = environ.get('HTTP_ORIGIN', '')
    
    # Origin     origin ,     origin 
    allowed_origin = origin if origin in allowed_origins else allowed_origins[0]
    
    return [
        ('Access-Control-Allow-Origin', allowed_origin),
        ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, X-CSRFToken'),
        ('Access-Control-Allow-Credentials', 'true'),
    ]

def application(environ, start_response):
    """ WSGI """
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # CORS preflight 
    if method == 'OPTIONS':
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
        ] + cors_headers(environ))
        return [b'{}']
    
    #  
    if path in ['/health/', '/api/health/', '/']:
        response_data = {
            "status": "emergency_mode",
            "message": "Django      ",
            "timestamp": os.environ.get('RAILWAY_DEPLOYMENT_ID', 'unknown'),
            "endpoints": {
                "health": "/health/",
                "api_health": "/api/health/",
                "debug": "/debug/"
            }
        }
        
        response_body = json.dumps(response_data, ensure_ascii=False, indent=2).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json; charset=utf-8'),
        ] + cors_headers(environ))
        return [response_body]
    
    #  API    
    elif path == '/api/projects/project_list/' or path == '/api/projects/':
        mock_projects = {
            "results": [],
            "message": " :     ",
            "emergency_mode": True
        }
        response_body = json.dumps(mock_projects, ensure_ascii=False).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json; charset=utf-8'),
        ] + cors_headers(environ))
        return [response_body]
    
    elif path.startswith('/api/users/notifications'):
        mock_notifications = {
            "results": [],
            "count": 0,
            "message": " :     ",
            "emergency_mode": True
        }
        response_body = json.dumps(mock_notifications, ensure_ascii=False).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json; charset=utf-8'),
        ] + cors_headers(environ))
        return [response_body]
    
    elif path == '/api/projects/invitations/' or path.startswith('/api/projects/') and 'invitations' in path:
        mock_invitations = {
            "results": [],
            "message": " :     ",
            "emergency_mode": True
        }
        response_body = json.dumps(mock_invitations, ensure_ascii=False).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json; charset=utf-8'),
        ] + cors_headers(environ))
        return [response_body]
    
    elif path.startswith('/api/users/') and method == 'GET':
        mock_user = {
            "id": 0,
            "email": "emergency@mode.com",
            "nickname": "",
            "profile_image": None,
            "message": " :     ",
            "emergency_mode": True
        }
        response_body = json.dumps(mock_user, ensure_ascii=False).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json; charset=utf-8'),
        ] + cors_headers(environ))
        return [response_body]
    
    elif path.startswith('/api/'):
        #   API    
        mock_response = {
            "message": " :  API    ",
            "path": path,
            "method": method,
            "emergency_mode": True,
            "status": "service_unavailable"
        }
        response_body = json.dumps(mock_response, ensure_ascii=False).encode('utf-8')
        start_response('503 Service Unavailable', [
            ('Content-Type', 'application/json; charset=utf-8'),
        ] + cors_headers(environ))
        return [response_body]
    
    #  
    elif path == '/debug/':
        debug_info = {
            "environment_variables": {
                "DJANGO_SETTINGS_MODULE": os.environ.get('DJANGO_SETTINGS_MODULE'),
                "DATABASE_URL": os.environ.get('DATABASE_URL', '')[:50] + '...' if os.environ.get('DATABASE_URL') else None,
                "SECRET_KEY": os.environ.get('SECRET_KEY', '')[:10] + '...' if os.environ.get('SECRET_KEY') else None,
                "RAILWAY_ENVIRONMENT": os.environ.get('RAILWAY_ENVIRONMENT'),
                "PORT": os.environ.get('PORT'),
            },
            "request_info": {
                "method": method,
                "path": path,
                "remote_addr": environ.get('REMOTE_ADDR'),
                "user_agent": environ.get('HTTP_USER_AGENT'),
            }
        }
        
        response_body = json.dumps(debug_info, ensure_ascii=False, indent=2).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json; charset=utf-8'),
        ] + cors_headers(environ))
        return [response_body]
    
    # 404 - Not Found
    else:
        error_response = {
            "error": "Not Found",
            "message": f"Path '{path}' not found in emergency server",
            "available_paths": ["/health/", "/api/health/", "/debug/"]
        }
        
        response_body = json.dumps(error_response, ensure_ascii=False, indent=2).encode('utf-8')
        start_response('404 Not Found', [
            ('Content-Type', 'application/json; charset=utf-8'),
        ] + cors_headers(environ))
        return [response_body]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"    -  {port}")
    print(f": http://localhost:{port}/health/")
    print(f": http://localhost:{port}/debug/")
    
    with make_server('', port, application) as httpd:
        httpd.serve_forever()