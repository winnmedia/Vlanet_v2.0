"""
    
SQL , XSS, CSRF    
"""
import re
import logging
from functools import wraps
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse

logger = logging.getLogger('security')


class SecurityError(Exception):
    """  """
    pass


def sanitize_input(value, field_type='text'):
    """
     
    SQL   XSS  
    """
    if value is None:
        return None
    
    #  
    value = str(value)
    
    # SQL   
    sql_patterns = [
        r"(\bunion\b.*\bselect\b|\bselect\b.*\bfrom\b|\binsert\b.*\binto\b|\bupdate\b.*\bset\b|\bdelete\b.*\bfrom\b)",
        r"(;|\"|'|--|\/\*|\*\/|xp_|sp_|0x|\\x)",
        r"(\bdrop\b|\bcreate\b|\balter\b|\btruncate\b|\bexec\b|\bexecute\b)",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f"SQL injection attempt detected: {value[:50]}...")
            raise SecurityError(" .")
    
    # XSS  
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
        r"<link",
        r"eval\(",
        r"alert\(",
        r"document\.cookie",
        r"window\.location",
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(f"XSS attempt detected: {value[:50]}...")
            raise SecurityError(" .")
    
    #    
    if field_type == 'email':
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
            raise SecurityError("   .")
    
    elif field_type == 'number':
        try:
            int(value)
        except ValueError:
            raise SecurityError("  .")
    
    elif field_type == 'alphanumeric':
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise SecurityError(", , _, -   .")
    
    return value


def secure_query(model, **kwargs):
    """
      
    Django ORM  SQL  
    """
    #  lookup  
    dangerous_lookups = ['regex', 'iregex']
    
    for key in kwargs.keys():
        lookup_parts = key.split('__')
        if len(lookup_parts) > 1 and lookup_parts[-1] in dangerous_lookups:
            raise SecurityError("     .")
    
    #   
    try:
        return model.objects.filter(**kwargs)
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise SecurityError("    .")


def rate_limit(max_requests=10, window=60):
    """
    Rate limiting 
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            from django.core.cache import cache
            
            # IP   rate limiting
            client_ip = request.META.get('REMOTE_ADDR', '')
            cache_key = f"rate_limit:{func.__name__}:{client_ip}"
            
            #    
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= max_requests:
                return JsonResponse({
                    "message": "   .    .",
                    "code": "RATE_LIMITED"
                }, status=429)
            
            #   
            cache.set(cache_key, current_requests + 1, window)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_file_upload(file):
    """
       
    """
    #    (50MB)
    max_size = 50 * 1024 * 1024
    if file.size > max_size:
        raise SecurityError("  50MB   .")
    
    #  
    allowed_extensions = [
        'jpg', 'jpeg', 'png', 'gif', 'webp',  # 
        'mp4', 'avi', 'mov', 'wmv', 'flv',    # 
        'mp3', 'wav', 'ogg',                   # 
        'pdf', 'doc', 'docx', 'xls', 'xlsx',   # 
        'zip', 'rar', '7z',                    # 
    ]
    
    #  
    file_ext = file.name.split('.')[-1].lower()
    if file_ext not in allowed_extensions:
        raise SecurityError(f"   : .{file_ext}")
    
    # MIME  
    import magic
    try:
        file_mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  #   
        
        # MIME    
        mime_extension_map = {
            'image/jpeg': ['jpg', 'jpeg'],
            'image/png': ['png'],
            'image/gif': ['gif'],
            'image/webp': ['webp'],
            'video/mp4': ['mp4'],
            'application/pdf': ['pdf'],
            # ...    
        }
        
        if file_mime in mime_extension_map:
            if file_ext not in mime_extension_map[file_mime]:
                raise SecurityError("    .")
    except Exception:
        # python-magic   
        pass
    
    #  
    import os
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', os.path.basename(file.name))
    
    return safe_filename


def secure_headers_middleware(get_response):
    """
       
    """
    def middleware(request):
        response = get_response(request)
        
        #   
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP  (Content Security Policy)
        if not hasattr(response, 'has_csp'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://videoplanet.up.railway.app wss://videoplanet.up.railway.app; "
            )
        
        return response
    
    return middleware


#    
def set_secure_cookie(response, key, value, max_age=None):
    """
       
    """
    from django.conf import settings
    
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age or (30 * 24 * 60 * 60),  #  30
        httponly=True,  # JavaScript  
        secure=not settings.DEBUG,  # HTTPS 
        samesite='Lax',  # CSRF  
        path='/',
    )
    
    return response