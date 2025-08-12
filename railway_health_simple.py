#!/usr/bin/env python3
"""
Ultra-Simple Health Check Server for Railway
Zero dependencies, immediate response
"""
import os
from wsgiref.simple_server import make_server, demo_app

def health_app(environ, start_response):
    """Simple WSGI application that always returns 200 OK"""
    path = environ.get('PATH_INFO', '/')
    
    # Health check paths
    if path in ['/', '/health/', '/api/health/', '/healthz/']:
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [b'{"status":"healthy","service":"videoplanet","timestamp":"2025-08-12"}']
    
    # Other paths return 404
    status = '404 Not Found'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b'Not Found']

# WSGI application
application = health_app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting health check server on port {port}")
    with make_server('', port, application) as httpd:
        httpd.serve_forever()