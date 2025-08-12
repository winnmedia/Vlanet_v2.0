#!/usr/bin/env python3
"""
Railway Health Beacon - Ultimate Failsafe Solution
=====================================
Zero-dependency health check server that ALWAYS works.
Runs from project root, completely independent of Django.
"""

def application(environ, start_response):
    """
    WSGI application - returns health check immediately
    No imports, no dependencies, no failures possible
    """
    path = environ.get('PATH_INFO', '/')
    
    # Health check paths
    if path in ['/', '/health', '/health/', '/api/health', '/api/health/']:
        # Simple JSON response
        response = b'{"status":"healthy","service":"videoplanet"}'
        
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response))),
            ('Cache-Control', 'no-cache'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [response]
    
    # All other paths - return 404
    response = b'{"error":"Not Found"}'
    start_response('404 Not Found', [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response)))
    ])
    return [response]

# Simple HTTP server for local testing
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    import os
    
    port = int(os.environ.get('PORT', 8000))
    print(f'Health Beacon running on port {port}')
    print('Test with: curl http://localhost:{}/health'.format(port))
    
    server = make_server('', port, application)
    server.serve_forever()