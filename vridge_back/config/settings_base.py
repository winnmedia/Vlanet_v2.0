"""
Base settings for vridge project.
"""
import os
from pathlib import Path
from datetime import timedelta

try:
    import environ
except ImportError:
    environ = None

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
if environ:
    try:
        env = environ.Env(
            DEBUG=(bool, False)
        )
        env_file = os.path.join(BASE_DIR, '.env')
        if os.path.exists(env_file):
            environ.Env.read_env(env_file)
    except Exception as e:
        environ = None

# environ      
if not environ:
    class MockEnv:
        def __init__(self):
            pass
        def __call__(self, key, default=None):
            return os.environ.get(key, default)
        def list(self, key, default=None):
            value = os.environ.get(key, '')
            if value:
                return [item.strip() for item in value.split(',')]
            return default or []
    env = MockEnv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default=os.environ.get('SECRET_KEY'))

#   SECRET_KEY 
if not DEBUG and SECRET_KEY:
    from .security_settings import validate_secret_key
    try:
        validate_secret_key(SECRET_KEY)
    except ValueError:
        # Railway     
        if 'RAILWAY_ENVIRONMENT' in os.environ:
            pass
        else:
            raise

# JWT Algorithm for authentication
ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')

# Google Gemini API Key
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

# Frontend URL for email links
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://vlanet.net')

# OpenAI API Key (for DALL-E image generation)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Hugging Face API Key (for Stable Diffusion image generation)
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')

# Twelve Labs API Key (for video understanding)
TWELVE_LABS_API_KEY = os.environ.get('TWELVE_LABS_API_KEY', '')

# EXAONE API Key  - Gemini 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS  
from .security_settings import get_allowed_hosts
ALLOWED_HOSTS = get_allowed_hosts()

#   
from .security_settings import get_secure_settings
secure_settings = get_secure_settings(DEBUG)
for key, value in secure_settings.items():
    globals()[key] = value

# Application definition
DJANGO_APPS = [
    # "daphne",  # Temporarily disabled - missing module
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

PROJECT_APPS = [
    "core",
    "users",
    "projects",
    "feedbacks",
    "onlines",
    "video_planning",
    "video_analysis",
    "ai_video",
    "admin_dashboard",
    "documents",
    "calendars",
    "invitations",  # 활성화 - 초대 기능 필수
    "analytics",
]

THIRD_PARTY_APPS = [
    # "channels",  # Temporarily disabled - missing module
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    # Railway health check middleware - MUST be first for quick response
    "config.middleware.RailwayHealthCheckMiddleware",
    
    # Unified CORS middleware - handles all CORS responses
    "config.middleware_cors_unified.UnifiedCORSMiddleware",  # Single source of CORS truth
    
    # Django security and session middleware
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    
    # Django standard middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # Monitoring and performance middleware
    "config.middleware.PerformanceMonitoringMiddleware",  # Performance monitoring
    "config.middleware.SecurityHeadersMiddleware",  # Security headers
    
    # Debug middleware (only in DEBUG mode)
    # "config.middleware_cors_unified.CORSDebugMiddleware",  # Enable for CORS debugging
    
    # Rate limiting and audit middleware (disabled for Railway stability)
    # "config.rate_limit_middleware.RateLimitMiddleware",
    # "config.rate_limit_middleware.SecurityAuditMiddleware",
    # "feedbacks.middleware.MediaHeadersMiddleware",
    # "projects.middleware.IdempotencyMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
            ],
        },
    },
]

# ASGI Configuration
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

# Channel Layers
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(env('REDIS_HOST', default='127.0.0.1'), env.int('REDIS_PORT', default=6379))],
        },
    },
}

# Database
import dj_database_url

DATABASE_URL = env('DATABASE_URL', default=None)

if DATABASE_URL:
    # Railway Heroku   DATABASE_URL 
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    #     
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get('DB_NAME', 'videoplanet'),
            "USER": os.environ.get('DB_USER', 'postgres'),
            "PASSWORD": os.environ.get('DB_PASSWORD', 'postgres'),
            "HOST": os.environ.get('DB_HOST', 'localhost'),
            "PORT": os.environ.get('DB_PORT', '5432'),
            "OPTIONS": {
                "connect_timeout": 10,
            }
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Static files directories
STATICFILES_DIRS = []

# Django static directory (if exists)
django_static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(django_static_dir):
    STATICFILES_DIRS.append(django_static_dir)

# Frontend build static directory (only if exists - for production)
frontend_static_dir = os.path.join(BASE_DIR, "../vridge_front/build/static")
if os.path.exists(frontend_static_dir):
    STATICFILES_DIRS.append(frontend_static_dir)
    
# Next.js .next/static directory (for development)
nextjs_static_dir = os.path.join(BASE_DIR, "../vridge_front/.next/static")
if os.path.exists(nextjs_static_dir):
    STATICFILES_DIRS.append(nextjs_static_dir)

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# WhiteNoise configuration
WHITENOISE_ROOT = os.path.join(BASE_DIR, "../vridge_front/build")
WHITENOISE_AUTOREFRESH = DEBUG

# AWS Settings
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', None)
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-2')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# URL configuration
APPEND_SLASH = True

# Cache configuration (moved to line 241 for Redis)

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=28),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": os.environ.get('JWT_ALGORITHM', 'HS256'),
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}

# CORS settings are now handled by config.cors_solution.RailwayCORSMiddleware
# Old django-cors-headers settings removed to avoid conflicts

# Email settings
from .email_settings import configure_email_settings
email_config = configure_email_settings()
EMAIL_BACKEND = email_config['EMAIL_BACKEND']
EMAIL_HOST = email_config['EMAIL_HOST']
EMAIL_PORT = email_config['EMAIL_PORT']
EMAIL_USE_TLS = email_config['EMAIL_USE_TLS']
EMAIL_HOST_USER = email_config['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = email_config['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = email_config['DEFAULT_FROM_EMAIL']

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 629145600  # 600MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 629145600  # 600MB

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Social Login Settings
NAVER_CLIENT_ID = env('NAVER_CLIENT_ID', default='')
NAVER_CLIENT_SECRET = env('NAVER_CLIENT_SECRET', default='')
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET', default='')
KAKAO_API_KEY = env('KAKAO_API_KEY', default='')

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Cache Configuration
# Redis     
try:
    import django_redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"redis://{os.environ.get('REDIS_HOST', '127.0.0.1')}:{os.environ.get('REDIS_PORT', '6379')}/1",
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,
                    'retry_on_timeout': True,
                },
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            },
            'KEY_PREFIX': 'vridge',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }
except ImportError:
    # Redis    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_cache_table',
        }
    }

# Session Configuration
try:
    import django_redis
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
except ImportError:
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Celery Configuration
CELERY_BROKER_URL = f"redis://{os.environ.get('REDIS_HOST', '127.0.0.1')}:{os.environ.get('REDIS_PORT', '6379')}/0"
CELERY_RESULT_BACKEND = f"redis://{os.environ.get('REDIS_HOST', '127.0.0.1')}:{os.environ.get('REDIS_PORT', '6379')}/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 3600  # 1 hour
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# CORS Settings - These are now handled by config.cors_solution.RailwayCORSMiddleware
# The new middleware provides more reliable CORS handling for Railway deployment
# Settings are kept here for reference but not actively used by django-cors-headers
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://vlanet-v1-0.vercel.app",
    "https://videoplanet.up.railway.app",
    "https://vlanet.net",
    "https://www.vlanet.net",
    "https://api.vlanet.net",
    "https://videoplanet-seven.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://vlanet-v1-0.vercel.app",
    "https://videoplanet.up.railway.app",
    "https://vlanet.net",
    "https://www.vlanet.net",
]

# Session and CSRF cookie settings
#   security_settings.py    
CSRF_COOKIE_HTTPONLY = False  # JavaScript CSRF   
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24
SESSION_SAVE_EVERY_REQUEST = True  #    

# Rate Limiting  ( -  )
RATE_LIMITING_ENABLED = env('RATE_LIMITING_ENABLED', default=not DEBUG)

# IP  (  )
RATE_LIMIT_WHITELIST_IPS = env.list('RATE_LIMIT_WHITELIST_IPS', default=[
    '127.0.0.1',
    '::1',
])

#   
RATE_LIMIT_TEST_ACCOUNTS = env.list('RATE_LIMIT_TEST_ACCOUNTS', default=[])

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}