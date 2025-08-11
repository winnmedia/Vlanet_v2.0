#  CORS  -  
from .railway import *

# Railway     
if 'CACHES' in locals():
    print(f"[CORS Emergency Fix] Cache backend: {CACHES.get('default', {}).get('BACKEND', 'Not configured')}")
else:
    print("[CORS Emergency Fix] WARNING: No cache configuration found!")

# CORS    
if 'corsheaders' not in INSTALLED_APPS:
    INSTALLED_APPS.insert(0, 'corsheaders')

#   
MIDDLEWARE = [
    'middleware.force_cors.ForceCorsMiddleware',  #  CORS 
    'corsheaders.middleware.CorsMiddleware',      # django-cors-headers
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS  -  
CORS_ALLOW_ALL_ORIGINS = True  #   origin 
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['*']  #   
CORS_ALLOW_HEADERS = ['*']  #   

# CSRF  
CSRF_TRUSTED_ORIGINS = [
    'https://vlanet.net',
    'https://www.vlanet.net',
    'https://*.railway.app',
    'https://*.vercel.app',
]

#    (CORS  )
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

#   
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = 'VideoPlanet <vridgeofficial@gmail.com>'

import logging
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("[CORS Emergency Fix] Settings loaded")
logger.info(f"CORS_ALLOW_ALL_ORIGINS: {CORS_ALLOW_ALL_ORIGINS}")
logger.info(f"Middleware count: {len(MIDDLEWARE)}")
logger.info(f"First middleware: {MIDDLEWARE[0]}")
logger.info("=" * 80)