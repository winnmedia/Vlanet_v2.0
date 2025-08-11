# SendGrid  
from .railway_cors_fix import *
import os

# CORS   
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS 
    'middleware.cors_debug.CorsDebugMiddleware',  # CORS 
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS    
print(f"[SendGrid Config] CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
print(f"[SendGrid Config] CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")

#  CORS  
CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'X-CSRFToken',
]

# SendGrid 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # SendGrid  'apikey' 
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')

#   
DEFAULT_FROM_EMAIL = 'VideoPlanet <vridgeofficial@gmail.com>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

#   
import logging
logger = logging.getLogger(__name__)

if EMAIL_HOST_PASSWORD:
    logger.info(f"SendGrid configured with API key: {EMAIL_HOST_PASSWORD[:10]}...")
    print(f"SendGrid API Key configured: {EMAIL_HOST_PASSWORD[:10]}...")
else:
    logger.error("SendGrid API key not found in SENDGRID_API_KEY environment variable")
    print("ERROR: SendGrid API key not configured!")

#    
EMAIL_TIMEOUT = 30