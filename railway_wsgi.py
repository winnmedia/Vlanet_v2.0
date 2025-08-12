#!/usr/bin/env python
"""
Railway WSGI Application Wrapper
Chief Architect's Solution for Railway Deployment

This wrapper handles the path resolution between Railway's root execution
and Django's subdirectory structure.
"""

import os
import sys
from pathlib import Path

# =============================================================================
# PATH RESOLUTION - Critical for Railway Deployment
# =============================================================================
# Add vridge_back to Python path to enable proper module imports
PROJECT_ROOT = Path(__file__).resolve().parent
DJANGO_ROOT = PROJECT_ROOT / 'vridge_back'

# Ensure Django app directory is in Python path
if str(DJANGO_ROOT) not in sys.path:
    sys.path.insert(0, str(DJANGO_ROOT))

# Set working directory to Django root
os.chdir(str(DJANGO_ROOT))

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
# Railway provides RAILWAY_ENVIRONMENT variable
# We use this to determine which settings module to use
if os.environ.get('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
else:
    # Local development fallback
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')

# =============================================================================
# DJANGO INITIALIZATION
# =============================================================================
try:
    from django.core.wsgi import get_wsgi_application
    from django.core.management import execute_from_command_line
    
    # Initialize Django WSGI application
    application = get_wsgi_application()
    
    print(f"✅ Railway WSGI initialized successfully")
    print(f"   Django Root: {DJANGO_ROOT}")
    print(f"   Settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"   Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    
except Exception as e:
    print(f"❌ Failed to initialize Django WSGI: {e}")
    import traceback
    traceback.print_exc()
    
    # Fallback health check application
    def application(environ, start_response):
        """Emergency fallback application for health checks"""
        path = environ.get('PATH_INFO', '/')
        
        if path in ['/health/', '/api/health/', '/healthz/', '/']:
            status = '200 OK'
            headers = [('Content-Type', 'application/json')]
            start_response(status, headers)
            return [b'{"status": "degraded", "error": "Django initialization failed"}']
        
        status = '503 Service Unavailable'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'Service temporarily unavailable - Django initialization failed']