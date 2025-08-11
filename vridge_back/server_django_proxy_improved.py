#!/usr/bin/env python3
"""
Improved Django Proxy Server with Enhanced Reliability
"""
import os
import sys
import subprocess
import threading
import time
import socket
import signal
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import http.client
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DJANGO_PORT = int(os.environ.get('DJANGO_PORT', '8001'))
PROXY_PORT = int(os.environ.get('PORT', '8000'))
MAX_RETRIES = 5
RETRY_DELAY = 2

class DjangoManager:
    """Manages Django process lifecycle"""
    
    def __init__(self):
        self.process = None
        self.is_ready = False
        self.restart_count = 0
        self.max_restarts = 10
        
    def start(self):
        """Start Django with automatic restart on failure"""
        logger.info("Starting Django process...")
        
        # Set environment
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'config.settings.railway'
        
        # Run migrations first
        try:
            logger.info("Running database migrations...")
            subprocess.run(
                [sys.executable, 'manage.py', 'migrate', '--noinput'],
                env=env,
                capture_output=True,
                timeout=60,
                check=False
            )
        except Exception as e:
            logger.warning(f"Migration warning: {e}")
        
        # Start Gunicorn with optimized settings
        cmd = [
            'gunicorn',
            'config.wsgi:application',
            f'--bind=127.0.0.1:{DJANGO_PORT}',
            '--workers=4',
            '--threads=2',
            '--worker-class=gthread',
            '--timeout=120',
            '--keepalive=5',
            '--max-requests=1000',
            '--max-requests-jitter=50',
            '--access-logfile=-',
            '--error-logfile=-',
            '--log-level=info',
            '--preload'
        ]
        
        self.process = subprocess.Popen(cmd, env=env)
        logger.info(f"Django process started with PID {self.process.pid}")
        
        # Monitor process
        monitor_thread = threading.Thread(target=self.monitor, daemon=True)
        monitor_thread.start()
        
    def monitor(self):
        """Monitor Django process and restart if needed"""
        while True:
            if self.process and self.process.poll() is not None:
                logger.error(f"Django process died with code {self.process.returncode}")
                
                if self.restart_count < self.max_restarts:
                    self.restart_count += 1
                    logger.info(f"Restarting Django (attempt {self.restart_count}/{self.max_restarts})")
                    time.sleep(RETRY_DELAY)
                    self.start()
                else:
                    logger.critical("Max restart attempts reached. Manual intervention required.")
                    sys.exit(1)
            
            # Check if Django is responding
            self.is_ready = self.check_django_health()
            time.sleep(5)
    
    def check_django_health(self):
        """Check if Django is healthy"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', DJANGO_PORT))
            sock.close()
            return result == 0
        except:
            return False
    
    def stop(self):
        """Gracefully stop Django"""
        if self.process:
            logger.info("Stopping Django process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Django didn't stop gracefully, forcing...")
                self.process.kill()


class ImprovedProxyHandler(BaseHTTPRequestHandler):
    """Enhanced proxy handler with better error handling"""
    
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def do_OPTIONS(self):
        """Handle CORS preflight properly"""
        self.send_response(200)
        origin = self.headers.get('Origin')
        
        # Only allow specific origins
        allowed_origins = [
            'https://vlanet.net',
            'https://www.vlanet.net',
            'https://videoplanet-seven.vercel.app'
        ]
        
        if origin in allowed_origins:
            self.send_header('Access-Control-Allow-Origin', origin)
        else:
            # Don't send CORS headers for unauthorized origins
            pass
            
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def handle_request(self):
        """Handle incoming requests with improved routing"""
        
        # Add security headers to all responses
        self.send_security_headers = True
        
        # Health check paths - immediate response
        if self.path in ['/', '/health', '/healthz']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.add_security_headers()
            self.end_headers()
            response = {
                'status': 'healthy',
                'timestamp': time.time(),
                'service': 'proxy'
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Django readiness check
        if self.path == '/ready':
            if django_manager.is_ready:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.add_security_headers()
                self.end_headers()
                response = {
                    'status': 'ready',
                    'django': 'active',
                    'restarts': django_manager.restart_count
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Retry-After', '5')
                self.add_security_headers()
                self.end_headers()
                response = {
                    'status': 'starting',
                    'message': 'Django is starting, please wait...'
                }
                self.wfile.write(json.dumps(response).encode())
            return
        
        # API requests - proxy to Django
        if self.path.startswith('/api/'):
            if not django_manager.is_ready:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Retry-After', '5')
                self.add_security_headers()
                self.end_headers()
                response = {
                    'error': 'Service temporarily unavailable',
                    'message': 'Please retry in a few seconds'
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            try:
                self.proxy_to_django()
            except Exception as e:
                logger.error(f"Proxy error: {e}")
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.add_security_headers()
                self.end_headers()
                response = {
                    'error': 'Bad Gateway',
                    'message': 'Unable to connect to backend service'
                }
                self.wfile.write(json.dumps(response).encode())
            return
        
        # 404 for unknown paths
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.add_security_headers()
        self.end_headers()
        response = {
            'error': 'Not Found',
            'path': self.path
        }
        self.wfile.write(json.dumps(response).encode())
    
    def add_security_headers(self):
        """Add security headers to response"""
        if self.send_security_headers:
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('X-XSS-Protection', '1; mode=block')
            self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
            self.send_header('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
    
    def proxy_to_django(self):
        """Proxy request to Django with connection pooling"""
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else None
        
        # Create connection with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                conn = http.client.HTTPConnection('127.0.0.1', DJANGO_PORT, timeout=30)
                
                # Forward headers
                headers = {}
                for key, value in self.headers.items():
                    if key.lower() not in ['host', 'connection']:
                        headers[key] = value
                
                # Make request
                conn.request(self.command, self.path, body, headers)
                response = conn.getresponse()
                
                # Send response
                self.send_response(response.status)
                
                # Forward response headers
                for key, value in response.getheaders():
                    if key.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(key, value)
                
                # Add security headers
                self.add_security_headers()
                self.end_headers()
                
                # Stream response body
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                
                conn.close()
                return
                
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Proxy attempt {attempt + 1} failed: {e}")
                    time.sleep(RETRY_DELAY)
                else:
                    raise
    
    def log_message(self, format, *args):
        """Custom logging"""
        # Don't log health checks
        if '/health' not in format % args and '/' != self.path:
            logger.info(f"[{self.client_address[0]}] {format % args}")


# Global Django manager
django_manager = DjangoManager()


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down...")
    django_manager.stop()
    sys.exit(0)


def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("="*60)
    logger.info("VideoPlanet Django Integration Server (Improved)")
    logger.info(f"Proxy Port: {PROXY_PORT}")
    logger.info(f"Django Port: {DJANGO_PORT}")
    logger.info("="*60)
    
    # Start Django
    django_manager.start()
    
    # Wait for Django to be ready
    logger.info("Waiting for Django to be ready...")
    for i in range(60):  # Wait up to 60 seconds
        if django_manager.is_ready:
            logger.info("Django is ready!")
            break
        time.sleep(1)
    else:
        logger.warning("Django is taking longer than expected to start")
    
    # Start proxy server
    logger.info(f"Starting proxy server on port {PROXY_PORT}")
    server = HTTPServer(('', PROXY_PORT), ImprovedProxyHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        django_manager.stop()


if __name__ == '__main__':
    main()
