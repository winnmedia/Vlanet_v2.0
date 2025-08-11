#!/usr/bin/env python3
"""
Immediate Security and Performance Fixes for Django Integration
These fixes address critical issues identified in QA testing
"""

import os
import sys

def apply_security_fixes():
    """Apply critical security fixes to Django settings"""
    
    print("🔒 Applying Critical Security Fixes...")
    print("="*50)
    
    # Fix 1: Update railway.py settings
    railway_settings = """
# CRITICAL SECURITY FIXES - Applied by QA Team

import os
from django.core.exceptions import ImproperlyConfigured

# 1. SECRET_KEY - Must be set from environment
def get_secret_key():
    key = os.environ.get('DJANGO_SECRET_KEY')
    if not key:
        # For development only - production must have env var
        if os.environ.get('DJANGO_ENV') == 'development':
            return 'dev-only-key-change-in-production'
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY environment variable must be set in production"
        )
    if len(key) < 50:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be at least 50 characters long"
        )
    if 'insecure' in key.lower():
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY contains 'insecure' - please generate a new key"
        )
    return key

SECRET_KEY = get_secret_key()

# 2. CORS - Restrict to specific origins only
CORS_ALLOW_ALL_ORIGINS = False  # CRITICAL: Changed from True

CORS_ALLOWED_ORIGINS = [
    "https://vlanet.net",
    "https://www.vlanet.net",
    "https://videoplanet-seven.vercel.app",
]

# Add localhost only in development
if os.environ.get('DJANGO_ENV') == 'development':
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ])

# 3. ALLOWED_HOSTS - Restrict to specific hosts
ALLOWED_HOSTS = [
    'videoplanet.up.railway.app',
    '.railway.app',
]

# Add localhost only in development
if os.environ.get('DJANGO_ENV') == 'development':
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# 4. Security Headers - Add missing headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 5. Session Security
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JS access
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# 6. Additional Security Settings
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
"""
    
    print("📝 Security fixes prepared. To apply:")
    print("1. Update config/settings/railway.py with the fixes above")
    print("2. Set DJANGO_SECRET_KEY environment variable in Railway")
    print("3. Restart the application")
    print()
    
    return railway_settings


def create_improved_proxy_server():
    """Create an improved proxy server with better error handling"""
    
    improved_proxy = '''#!/usr/bin/env python3
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
'''
    
    print("🚀 Improved proxy server created")
    print("📝 To apply:")
    print("1. Save as 'server_django_proxy_improved.py'")
    print("2. Update Procfile to use the improved version")
    print("3. Deploy to Railway")
    
    return improved_proxy


def generate_environment_template():
    """Generate environment variable template for Railway"""
    
    env_template = """
# Railway Environment Variables Template
# Copy these to Railway dashboard

# CRITICAL - Must be set for production
DJANGO_SECRET_KEY=<generate-a-secure-50+-character-key>
DJANGO_ENV=production

# Database (Usually auto-configured by Railway)
DATABASE_URL=<auto-configured-by-railway>

# Redis Cache (Optional but recommended)
REDIS_URL=<redis-connection-string>

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<app-specific-password>
DEFAULT_FROM_EMAIL=noreply@videoplanet.com

# Security Settings
SECURE_SSL_REDIRECT=False  # Railway handles SSL
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Application Settings
DEBUG=False
DJANGO_PORT=8001

# Monitoring (Optional)
SENTRY_DSN=<sentry-dsn-if-using>
NEW_RELIC_LICENSE_KEY=<new-relic-key-if-using>
"""
    
    print("📋 Environment Variables Template:")
    print(env_template)
    
    return env_template


def main():
    print("🔧 QA Team - Immediate Fixes and Improvements")
    print("="*60)
    print()
    
    # 1. Security Fixes
    security_fixes = apply_security_fixes()
    
    # Save security fixes
    with open('qa_security_fixes.py', 'w') as f:
        f.write(security_fixes)
    print("✅ Security fixes saved to: qa_security_fixes.py")
    print()
    
    # 2. Improved Proxy Server
    improved_proxy = create_improved_proxy_server()
    
    # Save improved proxy
    with open('server_django_proxy_improved.py', 'w') as f:
        f.write(improved_proxy)
    print("✅ Improved proxy saved to: server_django_proxy_improved.py")
    print()
    
    # 3. Environment Template
    env_template = generate_environment_template()
    
    # Save environment template
    with open('railway_env_template.txt', 'w') as f:
        f.write(env_template)
    print("✅ Environment template saved to: railway_env_template.txt")
    print()
    
    print("="*60)
    print("📌 IMMEDIATE ACTION ITEMS:")
    print("="*60)
    print()
    print("1. 🔴 CRITICAL - Security:")
    print("   - Apply security fixes to config/settings/railway.py")
    print("   - Set DJANGO_SECRET_KEY in Railway environment")
    print("   - Deploy immediately")
    print()
    print("2. ⚠️  HIGH - Reliability:")
    print("   - Replace proxy server with improved version")
    print("   - Update Procfile to use new server")
    print("   - Test in staging first if possible")
    print()
    print("3. 📊 MEDIUM - Monitoring:")
    print("   - Set up basic monitoring (uptime, response time)")
    print("   - Configure alerts for failures")
    print("   - Review logs daily")
    print()
    print("4. 📝 ONGOING - Documentation:")
    print("   - Document all configuration changes")
    print("   - Create runbook for common issues")
    print("   - Train team on new procedures")
    print()
    print("✅ All fixes and templates have been generated!")
    print("Please review and apply according to priority.")


if __name__ == "__main__":
    main()