#!/usr/bin/env python3
"""
Django    v2
      
"""
import os
import sys
import subprocess
import threading
import time
import socket
import json
import signal
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import http.client
from datetime import datetime

#   
class DjangoManager:
    def __init__(self):
        self.process = None
        self.port = int(os.environ.get('DJANGO_PORT', '8001'))
        self.status = "NOT_STARTED"
        self.error = None
        self.start_time = None
        self.health_check_count = 0
        self.last_health_check = None
        self.startup_logs = []
        
    def add_log(self, message):
        """  """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.startup_logs.append(log_entry)
        print(log_entry)
        
    def is_port_available(self):
        """   """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', self.port))
            sock.close()
            return result != 0  #   =   
        except Exception as e:
            self.add_log(f"Port check error: {e}")
            return True
            
    def check_django_health(self):
        """Django   """
        self.health_check_count += 1
        self.last_health_check = datetime.now()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', self.port))
            sock.close()
            
            if result == 0:
                #  Django  
                try:
                    conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=2)
                    conn.request("GET", "/api/health/")
                    response = conn.getresponse()
                    conn.close()
                    return response.status == 200
                except:
                    return False
            return False
        except Exception as e:
            self.add_log(f"Health check error: {e}")
            return False
    
    def start(self):
        """Django  """
        self.status = "STARTING"
        self.start_time = datetime.now()
        self.add_log("Starting Django initialization...")
        
        try:
            #  
            if not self.is_port_available():
                self.add_log(f"Port {self.port} is already in use, attempting to kill existing process...")
                self.kill_port_process()
                time.sleep(2)
            
            #   
            env = os.environ.copy()
            env['DJANGO_SETTINGS_MODULE'] = 'config.settings.railway'
            env['PYTHONUNBUFFERED'] = '1'
            
            #   
            self.add_log("Testing database connection...")
            db_test = subprocess.run(
                [sys.executable, 'manage.py', 'dbshell', '--command=SELECT 1;'],
                env=env,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if db_test.returncode != 0:
                self.add_log(f"Database connection failed: {db_test.stderr}")
                #     (SQLite fallback )
            else:
                self.add_log("Database connection successful")
            
            #  
            self.add_log("Running database migrations...")
            migrate_result = subprocess.run(
                [sys.executable, 'manage.py', 'migrate', '--noinput'],
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if migrate_result.returncode != 0:
                self.add_log(f"Migration warning: {migrate_result.stderr[:500]}")
            else:
                self.add_log("Migrations completed successfully")
            
            # Static   (production)
            if not os.environ.get('DEBUG', 'False') == 'True':
                self.add_log("Collecting static files...")
                subprocess.run(
                    [sys.executable, 'manage.py', 'collectstatic', '--noinput'],
                    env=env,
                    capture_output=True,
                    timeout=30
                )
            
            # Gunicorn 
            self.add_log(f"Starting Gunicorn on port {self.port}...")
            cmd = [
                'gunicorn',
                'config.wsgi:application',
                f'--bind=127.0.0.1:{self.port}',
                '--workers=2',
                '--threads=4',
                '--timeout=120',
                '--access-logfile=-',
                '--error-logfile=-',
                '--log-level=info',
                '--capture-output',
                '--enable-stdio-inheritance'
            ]
            
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            #    
            def monitor_output():
                for line in self.process.stdout:
                    if line.strip():
                        self.add_log(f"[Gunicorn] {line.strip()}")
                        if "Booting worker" in line:
                            self.status = "RUNNING"
                        elif "ERROR" in line:
                            self.error = line.strip()
            
            monitor_thread = threading.Thread(target=monitor_output, daemon=True)
            monitor_thread.start()
            
            # Django  
            self.add_log("Waiting for Django to start...")
            max_attempts = 30
            for i in range(max_attempts):
                time.sleep(2)
                if self.check_django_health():
                    self.status = "RUNNING"
                    self.add_log(f"Django started successfully after {i*2} seconds")
                    return True
                    
                if self.process.poll() is not None:
                    #  
                    self.status = "FAILED"
                    self.error = f"Gunicorn process exited with code {self.process.returncode}"
                    self.add_log(self.error)
                    return False
                    
            self.status = "TIMEOUT"
            self.error = "Django failed to start within 60 seconds"
            self.add_log(self.error)
            return False
            
        except Exception as e:
            self.status = "ERROR"
            self.error = str(e)
            self.add_log(f"Fatal error: {e}")
            self.add_log(traceback.format_exc())
            return False
    
    def kill_port_process(self):
        """    """
        try:
            result = subprocess.run(
                f"lsof -ti:{self.port} | xargs kill -9",
                shell=True,
                capture_output=True
            )
            self.add_log(f"Killed process on port {self.port}")
        except:
            pass
    
    def stop(self):
        """Django  """
        if self.process:
            self.add_log("Stopping Django...")
            self.process.terminate()
            time.sleep(2)
            if self.process.poll() is None:
                self.process.kill()
            self.status = "STOPPED"
    
    def get_status(self):
        """  """
        uptime = None
        if self.start_time:
            uptime = str(datetime.now() - self.start_time).split('.')[0]
            
        return {
            "status": self.status,
            "port": self.port,
            "error": self.error,
            "uptime": uptime,
            "health_checks": self.health_check_count,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "is_healthy": self.check_django_health(),
            "startup_logs": self.startup_logs[-20:]  #  20 
        }

# Django  
django_manager = DjangoManager()

class ImprovedProxyHandler(BaseHTTPRequestHandler):
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
        #   - Railway 
        if self.path in ['/', '/health', '/healthz']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        # Django   
        if self.path == '/django-status':
            status = django_manager.get_status()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status, indent=2).encode())
            return
        
        # Django  
        if self.path == '/ready':
            if django_manager.status == "RUNNING" and django_manager.check_django_health():
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Django Ready')
            else:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                status = django_manager.get_status()
                self.wfile.write(json.dumps({
                    "status": "not_ready",
                    "django": status
                }, indent=2).encode())
            return
        
        # API  
        if self.path.startswith('/api/') or self.path.startswith('/admin/'):
            if django_manager.status != "RUNNING":
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                status = django_manager.get_status()
                self.wfile.write(json.dumps({
                    "error": "Service temporarily unavailable",
                    "details": status
                }, indent=2).encode())
                return
            
            try:
                self.proxy_to_django()
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Bad Gateway",
                    "details": str(e)
                }, indent=2).encode())
            return
        
        # 404 for other paths
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "Not Found",
            "path": self.path
        }).encode())
    
    def proxy_to_django(self):
        """Django  """
        #   
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else None
        
        # Django 
        conn = http.client.HTTPConnection('127.0.0.1', django_manager.port, timeout=30)
        
        #  
        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ['host', 'connection']:
                headers[key] = value
        
        #  
        conn.request(self.command, self.path, body, headers)
        
        #  
        response = conn.getresponse()
        
        #  
        self.send_response(response.status)
        for key, value in response.getheaders():
            if key.lower() not in ['connection', 'transfer-encoding']:
                self.send_header(key, value)
        self.end_headers()
        
        #  
        self.wfile.write(response.read())
        conn.close()
    
    def log_message(self, format, *args):
        #   
        message = format % args
        if not any(path in message for path in ['/', '/health', '/healthz']) or '/api/' in message:
            print(f"[PROXY] {message}")

def signal_handler(signum, frame):
    """ """
    print(f"\nReceived signal {signum}, shutting down...")
    django_manager.stop()
    sys.exit(0)

def main():
    #   
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    #  
    proxy_port = int(os.environ.get('PORT', '8000'))
    
    print("="*70)
    print("VideoPlanet Backend - Enhanced Django Integration v2")
    print(f"Proxy Port: {proxy_port} (Railway)")
    print(f"Django Port: {django_manager.port} (Internal)")
    print(f"Environment: {'DEBUG' if os.environ.get('DEBUG') == 'True' else 'PRODUCTION'}")
    print("="*70)
    
    # Django 
    print("\n[INIT] Starting Django server...")
    django_thread = threading.Thread(target=django_manager.start, daemon=True)
    django_thread.start()
    
    #   
    print(f"\n[INIT] Starting proxy server on port {proxy_port}...")
    server = HTTPServer(('', proxy_port), ImprovedProxyHandler)
    
    print(f"[READY] Server is running. Check status at /django-status")
    print(f"[READY] Health check at /")
    print(f"[READY] Django readiness at /ready")
    print("-"*70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        django_manager.stop()

if __name__ == '__main__':
    main()