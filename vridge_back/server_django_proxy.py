#!/usr/bin/env python3
"""
Django   
  , API  Django 
"""
import os
import sys
import subprocess
import threading
import time
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import http.client

# Django 
django_port = int(os.environ.get('DJANGO_PORT', '8001'))
django_starting = True

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def do_OPTIONS(self):
        # CORS preflight 
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def handle_request(self):
        global django_starting
        
        #    
        if self.path in ['/', '/health', '/healthz']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        # /ready  Django  
        if self.path == '/ready':
            if check_django():
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Django Ready')
            else:
                self.send_response(503)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Django Starting...')
            return
        
        # API  Django 
        if self.path.startswith('/api/'):
            if not check_django():
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Service starting, please wait..."}')
                return
            
            try:
                # Django 
                self.proxy_to_django()
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}"}}'.encode())
            return
        
        #    404
        self.send_response(404)
        self.end_headers()
    
    def proxy_to_django(self):
        """Django  """
        #   
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else None
        
        # Django 
        conn = http.client.HTTPConnection('127.0.0.1', django_port)
        
        #  
        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ['host']:
                headers[key] = value
        
        #  
        conn.request(self.command, self.path, body, headers)
        
        #  
        response = conn.getresponse()
        
        #   
        self.send_response(response.status)
        
        #   
        for key, value in response.getheaders():
            if key.lower() not in ['connection']:
                self.send_header(key, value)
        self.end_headers()
        
        #   
        self.wfile.write(response.read())
        
        conn.close()
    
    def log_message(self, format, *args):
        #   
        if '/' not in format % args or '/api/' in format % args:
            print(f"[PROXY] {format % args}")

def check_django():
    """Django  """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(('127.0.0.1', django_port))
        sock.close()
        return result == 0
    except:
        return False

def start_django():
    """Django """
    global django_starting
    
    print("[DJANGO] Preparing Django...")
    time.sleep(2)
    
    #   
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
    
    # 
    print("[DJANGO] Running migrations...")
    try:
        subprocess.run(
            [sys.executable, 'manage.py', 'migrate', '--noinput'],
            capture_output=True,
            timeout=30,
            check=False
        )
    except:
        pass
    
    # Gunicorn 
    print(f"[DJANGO] Starting Gunicorn on port {django_port}...")
    cmd = [
        'gunicorn',
        'config.wsgi:application',
        f'--bind=127.0.0.1:{django_port}',
        '--workers=2',
        '--threads=2',
        '--timeout=120',
        '--log-level=info'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"[DJANGO] Failed: {e}")
        django_starting = False

def main():
    #  
    proxy_port = int(os.environ.get('PORT', '8000'))
    
    print("="*60)
    print("VideoPlanet Backend with Django Integration")
    print(f"Proxy port: {proxy_port} (Railway)")
    print(f"Django port: {django_port} (Internal)")
    print("="*60)
    
    # Django  
    django_thread = threading.Thread(target=start_django, daemon=True)
    django_thread.start()
    
    #   
    print(f"[PROXY] Starting proxy server on port {proxy_port}")
    server = HTTPServer(('', proxy_port), ProxyHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()