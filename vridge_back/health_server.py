#!/usr/bin/env python3
"""
  
Railway    HTTP 
Django     
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
    """  """
    
    def log_message(self, format, *args):
        """  """
        sys.stdout.write(f"[HEALTH] {format % args}\n")
        sys.stdout.flush()
    
    def do_GET(self):
        """GET  """
        if self.path in ['/', '/health', '/healthz']:
            #   
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/ready':
            # Django    
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
        """HEAD  """
        self.do_GET()
    
    def do_OPTIONS(self):
        """OPTIONS   (CORS)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.end_headers()

def check_django_ready():
    """Django   """
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
    """  """
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"[HEALTH] Health check server running on port {port}")
    sys.stdout.flush()
    httpd.serve_forever()

if __name__ == '__main__':
    # Railway    
    health_port = int(os.environ.get('HEALTH_PORT', 8001))
    
    #   
    print(f"[HEALTH] Starting independent health check server...")
    run_health_server(health_port)