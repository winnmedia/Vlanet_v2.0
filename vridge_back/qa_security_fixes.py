
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
