#!/usr/bin/env python3
"""
Railway Smart Router - Ultimate Solution
========================================
Single entry point that routes requests intelligently.
Health checks get instant response, API calls go to Django.
Zero-dependency for health checks, full Django for API.
"""

import os
import sys
import time
import json
import logging
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Track Django initialization
django_app = None
django_loading = False
django_load_time = None

def load_django():
    """Load Django application in background"""
    global django_app, django_loading, django_load_time
    
    if django_loading or django_app:
        return
    
    django_loading = True
    start_time = time.time()
    
    try:
        # Add Django directory to path
        django_dir = os.path.join(os.path.dirname(__file__), 'vridge_back')
        if django_dir not in sys.path:
            sys.path.insert(0, django_dir)
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
        
        # Initialize Django
        import django
        django.setup()
        
        # Get WSGI application
        from django.core.wsgi import get_wsgi_application
        django_app = get_wsgi_application()
        
        django_load_time = time.time() - start_time
        logger.info(f"Django loaded successfully in {django_load_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Failed to load Django: {e}")
        django_loading = False

def application(environ, start_response):
    """
    WSGI Router Application
    Routes requests based on path pattern
    """
    global django_app
    
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # PHASE 1: Health Check - Instant Response
    health_paths = ['/', '/health', '/health/', '/api/health', '/api/health/', '/_health']
    
    if path in health_paths:
        uptime = time.time() - (django_load_time or 0) if django_load_time else 0
        
        response_data = {
            'status': 'healthy',
            'service': 'videoplanet-backend',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'uptime_seconds': round(uptime, 2),
            'django_ready': django_app is not None,
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
            'version': '1.0.0'
        }
        
        response_body = json.dumps(response_data, indent=2).encode('utf-8')
        
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body))),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('X-Service', 'health-beacon'),
            ('Access-Control-Allow-Origin', '*')
        ])
        
        return [response_body]
    
    # PHASE 2: CORS Preflight - Quick Response
    if method == 'OPTIONS':
        start_response('200 OK', [
            ('Content-Length', '0'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
            ('Access-Control-Max-Age', '86400')
        ])
        return [b'']
    
    # PHASE 3: API Requests - Route to Django
    if path.startswith('/api/') or path.startswith('/admin/') or path.startswith('/media/') or path.startswith('/static/'):
        # Load Django if not loaded
        if not django_app:
            load_django()
        
        # If Django is ready, use it
        if django_app:
            try:
                return django_app(environ, start_response)
            except Exception as e:
                logger.error(f"Django error: {e}")
                
                error_response = json.dumps({
                    'error': 'Internal Server Error',
                    'message': str(e),
                    'status': 500
                }).encode('utf-8')
                
                start_response('500 Internal Server Error', [
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(error_response))),
                    ('Access-Control-Allow-Origin', '*')
                ])
                return [error_response]
        else:
            # Django not ready yet
            retry_response = json.dumps({
                'error': 'Service Starting',
                'message': 'Please wait a moment and retry',
                'status': 503
            }).encode('utf-8')
            
            start_response('503 Service Unavailable', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(retry_response))),
                ('Retry-After', '5'),
                ('Access-Control-Allow-Origin', '*')
            ])
            return [retry_response]
    
    # PHASE 4: Unknown paths - 404
    not_found = json.dumps({
        'error': 'Not Found',
        'path': path,
        'status': 404
    }).encode('utf-8')
    
    start_response('404 Not Found', [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(not_found))),
        ('Access-Control-Allow-Origin', '*')
    ])
    return [not_found]

# Start Django loading in background when module loads
if __name__ != '__main__':
    import threading
    loader_thread = threading.Thread(target=load_django)
    loader_thread.daemon = True
    loader_thread.start()
    logger.info("Railway Router initialized - Django loading in background")

# For local testing
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    port = int(os.environ.get('PORT', 8000))
    print(f'Railway Router running on port {port}')
    print(f'Test health: curl http://localhost:{port}/health')
    print(f'Test API: curl http://localhost:{port}/api/videos/')
    
    server = make_server('', port, application)
    server.serve_forever()