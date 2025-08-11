"""
   
"""

import os
from django.conf import settings


def configure_security(app_settings):
    """
         
    settings     
    """
    
    #   
    is_production = not app_settings.DEBUG
    
    if is_production:
        # HTTPS 
        app_settings.SECURE_SSL_REDIRECT = True
        app_settings.SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        
        #  
        app_settings.SESSION_COOKIE_SECURE = True
        app_settings.CSRF_COOKIE_SECURE = True
        app_settings.SESSION_COOKIE_HTTPONLY = True
        app_settings.CSRF_COOKIE_HTTPONLY = True
        app_settings.SESSION_COOKIE_SAMESITE = 'Lax'
        app_settings.CSRF_COOKIE_SAMESITE = 'Lax'
        
        # HSTS (HTTP Strict Transport Security)
        app_settings.SECURE_HSTS_SECONDS = 31536000  # 1
        app_settings.SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        app_settings.SECURE_HSTS_PRELOAD = True
        
        #  
        app_settings.SECURE_CONTENT_TYPE_NOSNIFF = True
        app_settings.SECURE_BROWSER_XSS_FILTER = True
        app_settings.X_FRAME_OPTIONS = 'DENY'
        
        # Referrer Policy
        app_settings.SECURE_REFERRER_POLICY = 'same-origin'
        
        # CSP (Content Security Policy) 
        app_settings.CSP_DEFAULT_SRC = ("'self'",)
        app_settings.CSP_SCRIPT_SRC = (
            "'self'",
            "'unsafe-inline'",  # React    (  )
            "https://www.google-analytics.com",
            "https://www.googletagmanager.com",
        )
        app_settings.CSP_STYLE_SRC = (
            "'self'",
            "'unsafe-inline'",  #   
            "https://fonts.googleapis.com",
        )
        app_settings.CSP_FONT_SRC = (
            "'self'",
            "https://fonts.gstatic.com",
        )
        app_settings.CSP_IMG_SRC = (
            "'self'",
            "data:",
            "https:",
            "blob:",
        )
        app_settings.CSP_MEDIA_SRC = (
            "'self'",
            "blob:",
            "https:",
        )
        app_settings.CSP_CONNECT_SRC = (
            "'self'",
            "https://videoplanet.up.railway.app",
            "wss://videoplanet.up.railway.app",
            "https://www.google-analytics.com",
        )
    
    #   
    app_settings.AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 8,
            }
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
        {
            'NAME': 'users.validators.CustomPasswordValidator',
        },
    ]
    
    #  
    app_settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    app_settings.SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7
    
    #   
    app_settings.FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
    app_settings.DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
    app_settings.DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
    
    #   
    app_settings.ALLOWED_UPLOAD_EXTENSIONS = {
        'video': ['.mp4', '.mov', '.avi', '.wmv', '.mkv', '.webm'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'],
        'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
    }
    
    # Rate Limiting  (django-ratelimit  )
    app_settings.RATELIMIT_ENABLE = is_production
    app_settings.RATELIMIT_VIEW = '100/h'  #  100
    
    return app_settings


class SecurityMiddleware:
    """
        
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        #   
        if not settings.DEBUG:
            # Permissions Policy ( Feature Policy)
            response['Permissions-Policy'] = (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "accelerometer=()"
            )
            
            #   ( )
            if request.path.startswith('/api/') or request.path.startswith('/admin/'):
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
        
        return response


def check_security_headers(url):
    """
       
         
    """
    import requests
    
    print(f" {url}    ...")
    
    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        
        security_headers = {
            'Strict-Transport-Security': 'HSTS',
            'X-Content-Type-Options': 'Content Type Options',
            'X-Frame-Options': 'Frame Options',
            'X-XSS-Protection': 'XSS Protection',
            'Content-Security-Policy': 'CSP',
            'Referrer-Policy': 'Referrer Policy',
            'Permissions-Policy': 'Permissions Policy',
        }
        
        print("\n   :")
        found = []
        for header, name in security_headers.items():
            if header in headers:
                print(f"  - {name}: {headers[header][:50]}...")
                found.append(header)
        
        print("\n   :")
        missing = []
        for header, name in security_headers.items():
            if header not in headers:
                print(f"  - {name}")
                missing.append(header)
        
        #  
        score = len(found) / len(security_headers) * 100
        print(f"\n  : {score:.1f}%")
        
        if score >= 80:
            print("     !")
        elif score >= 60:
            print("       .")
        else:
            print("    .   .")
        
        return score
        
    except Exception as e:
        print(f"  : {e}")
        return 0


#    

def sanitize_user_input(text):
    """
      
    """
    import html
    import re
    
    if not text:
        return text
    
    # HTML  
    text = html.escape(text)
    
    #   
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text


def generate_secure_filename(filename):
    """
       
    """
    import re
    import secrets
    from pathlib import Path
    
    #   
    path = Path(filename)
    name = path.stem
    ext = path.suffix.lower()
    
    #   
    allowed_extensions = []
    for exts in settings.ALLOWED_UPLOAD_EXTENSIONS.values():
        allowed_extensions.extend(exts)
    
    if ext not in allowed_extensions:
        raise ValueError(f"   : {ext}")
    
    #   
    safe_name = re.sub(r'[^\w\s-]', '', name)
    safe_name = re.sub(r'[-\s]+', '-', safe_name)
    
    #   
    random_str = secrets.token_hex(4)
    
    return f"{safe_name}_{random_str}{ext}"


def check_file_content(file_obj):
    """
       (  )
    """
    import magic
    
    #    
    file_obj.seek(0)
    file_header = file_obj.read(1024)
    file_obj.seek(0)
    
    # MIME  
    mime = magic.from_buffer(file_header, mime=True)
    
    #  MIME   
    ext_mime_map = {
        '.jpg': ['image/jpeg'],
        '.jpeg': ['image/jpeg'],
        '.png': ['image/png'],
        '.gif': ['image/gif'],
        '.mp4': ['video/mp4'],
        '.pdf': ['application/pdf'],
        #    ...
    }
    
    file_ext = Path(file_obj.name).suffix.lower()
    allowed_mimes = ext_mime_map.get(file_ext, [])
    
    if mime not in allowed_mimes:
        raise ValueError(f"    : {mime}")
    
    return True