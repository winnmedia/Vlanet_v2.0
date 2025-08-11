# Railway CORS     
from .railway import *
import os

#  DEBUG   
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# CORS 
CORS_ALLOW_ALL_ORIGINS = False  #  origin 
CORS_ALLOW_CREDENTIALS = True

#  origin 
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

# CORS    (Vercel preview URLs )
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://vlanet.*\.vercel\.app$",
]

# Preflight   
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET', 
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

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
    'x-idempotency-key',  #    
]

# CORS preflight   ()
CORS_PREFLIGHT_MAX_AGE = 86400

print("CORS Fix settings loaded")
print(f"CORS_ALLOW_ALL_ORIGINS: {CORS_ALLOW_ALL_ORIGINS}")
print(f"CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")

# CSRF  
CSRF_TRUSTED_ORIGINS = [
    'https://vlanet.net',
    'https://www.vlanet.net',
    'https://*.railway.app',
    'https://videoplanetready.vercel.app',
    'https://vlanet-v1-0.vercel.app',
]

#   
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True