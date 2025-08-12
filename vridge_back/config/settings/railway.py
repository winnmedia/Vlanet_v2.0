"""
Railway  Django  
Production  
"""
import os
import dj_database_url
from ..settings_base import *

#  
SECRET_KEY = os.environ.get('SECRET_KEY', os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-production-key-change-me'))
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

#    (QA )
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
ALLOWED_HOSTS = [
    'videoplanet.up.railway.app',
    '.railway.app',
    'localhost',
    '127.0.0.1',
    '*',  #    
]

# CSRF  
CSRF_TRUSTED_ORIGINS = [
    'https://videoplanet.up.railway.app',
    'https://*.railway.app',
    'https://vlanet.net',
    'https://www.vlanet.net',
    'https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app',
    'https://vlanet-v2-0.vercel.app',
    'https://*.vercel.app',
    'http://localhost:3000',
    'http://localhost:3001',
]

# Railway PostgreSQL 연결 설정 (최적화된 설정)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Railway PostgreSQL 연결 최적화
    db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=0)  # 연결 풀링 비활성화로 500 에러 방지
    
    # Railway PostgreSQL 전용 옵션 설정
    db_config.update({
        'OPTIONS': {
            'sslmode': 'require',  # Railway는 SSL 필수
            'connect_timeout': 10,  # Reduced from 60 to fail faster
            'isolation_level': 2,  # READ COMMITTED (PostgreSQL default)
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
        },
        'CONN_MAX_AGE': 0,  # Railway에서 긴 연결은 문제를 일으킬 수 있음
        'ATOMIC_REQUESTS': False,  # Changed from True to avoid long transactions
        'AUTOCOMMIT': True,
        'TIME_ZONE': None,  # PostgreSQL 시간대 설정
    })
    
    DATABASES = {'default': db_config}
    
    # PostgreSQL 연결 안정성 로깅
    print(f"[DATABASE] PostgreSQL 연결 설정 완료: {db_config['HOST']}:{db_config['PORT']}")
    print(f"[DATABASE] 데이터베이스: {db_config['NAME']}, 사용자: {db_config['USER']}")
    print(f"[DATABASE] CONN_MAX_AGE: {db_config['CONN_MAX_AGE']}, SSL: {db_config['OPTIONS']['sslmode']}")
    
else:
    # Fallback to SQLite for local testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# CORS  - django-cors-headers 
CORS_ALLOW_ALL_ORIGINS = False  #  :  origin 
CORS_ALLOW_CREDENTIALS = True

#  origin  (  )
CORS_ALLOWED_ORIGINS = [
    "https://vlanet.net",
    "https://www.vlanet.net",
    "https://videoplanet-seven.vercel.app",
    "https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app",  # Vercel preview URL
    "https://vlanet-v2-0.vercel.app",  # Alternative Vercel URL
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# CORS URL patterns for Vercel dynamic deployments
CORS_URLS_REGEX = r'^/api/.*$'  # Apply CORS to all API routes

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
    'pragma',
    'x-idempotency-key',
]

#  
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'HEAD',
]

# Preflight  
CORS_PREFLIGHT_MAX_AGE = 86400

# CORS URL 정규식 패턴 (Vercel dynamic URLs)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://vlanet-v2-0-.*\.vercel\.app$",
    r"^https://.*-vlanets-projects\.vercel\.app$",
    r"^https://vlanet-.*\.vercel\.app$",
    r"^https://.*\.vercel\.app$",  # All Vercel deployments
]

#  
CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'X-CSRFToken',
    'Content-Length',
    'X-Request-ID',
    'Authorization',
]

# CORS Replace existing headers (important for Railway)
# CORS_REPLACE_HTTPS_REFERER removed - deprecated in newer django-cors-headers

#   
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Redis  
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
else:
    # Fallback to database cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }

#  
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@videoplanet.com')

#  
SECURE_SSL_REDIRECT = False  # Railway  
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATICFILES_DIRS - Railway environment specific paths
STATICFILES_DIRS = []

# Check for local static directory
static_dir = os.path.join(BASE_DIR, 'static')
if os.path.exists(static_dir):
    STATICFILES_DIRS.append(static_dir)
    print(f"[STATIC] Added local static directory: {static_dir}")

# Railway environment - frontend build might be in different locations
# Try multiple possible locations for frontend build
frontend_paths = [
    os.path.join(BASE_DIR, '../vridge_front/build/static'),  # Local dev path
    os.path.join(BASE_DIR, '../frontend/build/static'),      # Alternative path
    '/app/vridge_front/build/static',                        # Railway absolute path
    '/app/frontend/build/static',                            # Alternative Railway path
]

for frontend_path in frontend_paths:
    if os.path.exists(frontend_path):
        STATICFILES_DIRS.append(frontend_path)
        print(f"[STATIC] Found frontend static files at: {frontend_path}")
        break
else:
    print("[STATIC] Warning: No frontend build directory found")

# WhiteNoise configuration for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_AUTOREFRESH = DEBUG  # Enable auto-refresh in debug mode
WHITENOISE_USE_FINDERS = True   # Use Django's static file finders
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

#   (   )
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # SQL   
            'propagate': False,
        },
        'users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Sentry   (Railway 502   )

#    
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# REST Framework with Enhanced Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/min',  # Login rate limiting
        'signup': '3/hour',  # Signup rate limiting
    },
    # EXCEPTION_HANDLER는 제거 - 미들웨어에서 처리
    # 'EXCEPTION_HANDLER': 'core.error_handling.custom_exception_handler',
}

# JWT 
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# 설정 검증
import sys
import logging

# 로깅 설정 검증
logger = logging.getLogger('django')
logger.info(f"Railway settings loaded - DEBUG={DEBUG}")
logger.info(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
logger.info(f"CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS[:3]}...")
logger.info(f"Database configured: {'DATABASE_URL' in os.environ}")
logger.info(f"Redis configured: {'REDIS_URL' in os.environ}")