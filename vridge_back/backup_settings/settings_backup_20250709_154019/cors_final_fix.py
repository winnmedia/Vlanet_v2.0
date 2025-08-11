#  CORS  
from .sendgrid_config import *

# CORS   
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

#     
CORS_ALLOWED_ORIGINS = [
    "https://vlanet.net",
    "https://www.vlanet.net",
    "http://vlanet.net",
    "http://www.vlanet.net",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://videoplanetready.vercel.app",
    "https://vridge-front-production.up.railway.app",
    "https://vlanet-v1-0.vercel.app",
]

#   origin 
import os
additional_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if additional_origins:
    for origin in additional_origins.split(','):
        origin = origin.strip()
        if origin and origin not in CORS_ALLOWED_ORIGINS:
            CORS_ALLOWED_ORIGINS.append(origin)

# CORS  
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://vlanet.*\.vercel\.app$",
    r"^https://.*-winnmedia\.vercel\.app$",
]

#  HTTP  
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

#    
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
]

#  
CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'X-CSRFToken',
]

# Preflight 
CORS_PREFLIGHT_MAX_AGE = 86400

# CSRF    
CSRF_TRUSTED_ORIGINS = [
    'https://vlanet.net',
    'https://www.vlanet.net',
    'https://*.railway.app',
    'https://videoplanet.up.railway.app',
    'https://videoplanetready.vercel.app',
    'https://vlanet-v1-0.vercel.app',
    'https://*.vercel.app',
]

#    (CORS )
MIDDLEWARE = [
    'middleware.force_cors.ForceCorsMiddleware',  #  CORS  
    'corsheaders.middleware.CorsMiddleware',  # django-cors-headers
    'django.middleware.security.SecurityMiddleware',
    'middleware.cors_debug.CorsDebugMiddleware',  # CORS 
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#  
print("=" * 80)
print("[CORS Final Fix] Settings loaded")
print(f"CORS_ALLOWED_ORIGINS ({len(CORS_ALLOWED_ORIGINS)} origins):")
for origin in CORS_ALLOWED_ORIGINS:
    print(f"  - {origin}")
print(f"CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
print(f"CORS_ALLOW_ALL_ORIGINS: {CORS_ALLOW_ALL_ORIGINS}")
print("=" * 80)