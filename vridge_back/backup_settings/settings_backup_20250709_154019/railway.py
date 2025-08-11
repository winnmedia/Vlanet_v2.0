# Railway  Django 
import os
import dj_database_url
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Railway  
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None

#  
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")
ALGORITHM = os.environ.get('ALGORITHM', 'HS256')

#  
ALLOWED_HOSTS = [
    '.railway.app',
    'vlanet.net', 
    'www.vlanet.net',
    'localhost',
    '127.0.0.1'
]

# Application definition
DJANGO_APPS = [
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
    "video_analysis",
    "video_planning",
    "admin_dashboard",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

# users  auth   
INSTALLED_APPS = [
    # Project apps  ( users)
    "core",
    "users",
    "projects",
    "feedbacks",
    "onlines",
    "video_analysis",
    "video_planning",
    "admin_dashboard",
    
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Third party apps
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

#  (PostgreSQL)
# Railway RAILWAY_DATABASE_URL  DATABASE_URL  
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('RAILWAY_DATABASE_URL')

#     

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    #     
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

#   
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'frontend_build/static',
]

# WhiteNoise configuration for React SPA
WHITENOISE_ROOT = BASE_DIR / 'frontend_build'
WHITENOISE_AUTOREFRESH = DEBUG

# WhiteNoise  (collectstatic  )
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

#     
MEDIA_URL = '/media/'
# Railway    ,   
MEDIA_ROOT = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', BASE_DIR / 'media')

#     
import os as os_module
if not os_module.path.exists(MEDIA_ROOT):
    os_module.makedirs(MEDIA_ROOT, exist_ok=True)

# CORS 
#   CORS origin 
CORS_ALLOWED_ORIGINS_ENV = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOWED_ORIGINS_ENV = [origin.strip() for origin in CORS_ALLOWED_ORIGINS_ENV if origin.strip()]

#  CORS  
CORS_ALLOWED_ORIGINS_DEFAULT = [
    "https://vlanet.net",
    "https://www.vlanet.net",
    "http://vlanet.net",
    "http://www.vlanet.net",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://vridge-front-production.up.railway.app",
    "https://videoplanetready.vercel.app",
    "https://vlanet-v1-0.vercel.app",
]

#   
CORS_ALLOWED_ORIGINS = list(set(CORS_ALLOWED_ORIGINS_DEFAULT + CORS_ALLOWED_ORIGINS_ENV))

# CORS 

# CORS  
CORS_ALLOW_CREDENTIALS = True
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

# CORS_ALLOW_ALL_ORIGINS False  CORS_ALLOWED_ORIGINS 
CORS_ALLOW_ALL_ORIGINS = False

# CSRF    
CSRF_TRUSTED_ORIGINS = [
    'https://vlanet.net',
    'https://www.vlanet.net',
    'https://*.railway.app',
]

# REST Framework 
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

# JWT 
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=28),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

# Twelve Labs API 
TWELVE_LABS_API_KEY = os.environ.get('TWELVE_LABS_API_KEY')
TWELVE_LABS_INDEX_ID = os.environ.get('TWELVE_LABS_INDEX_ID')

#   
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_SECRET_KEY = os.environ.get('NAVER_SECRET_KEY')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
KAKAO_API_KEY = os.environ.get('KAKAO_API_KEY')

# Railway   
# Railway   , RAILWAY_VOLUME_MOUNT_PATH 

#   (SendGrid  Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SendGrid  
if os.environ.get('SENDGRID_API_KEY'):
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'apikey'  # SendGrid  'apikey' 
    EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    pass  # SendGrid configured
# Gmail  
else:
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', os.environ.get('GOOGLE_ID'))
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', os.environ.get('GOOGLE_APP_PASSWORD'))
    pass  # Gmail configured

#  
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'VideoPlanet <vridgeofficial@gmail.com>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

#   

# Sentry 
SENTRY_DSN = os.environ.get('SENTRY_DSN')

#  
AUTH_USER_MODEL = "users.User"

# WSGI  

#  
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

#  
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#   -    
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
    pass  # Redis cache configured
else:
    # Redis      
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_cache_table',
        }
    }
    pass  # Using database cache as fallback

# 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

#     