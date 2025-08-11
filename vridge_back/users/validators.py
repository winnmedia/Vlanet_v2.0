import re
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class InputValidator:
    """    """
    
    #   (RFC 5322   )
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    #  
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    
    @classmethod
    def validate_email(cls, email):
        """
          
        Returns: (is_valid: bool, error_message: str or None)
        """
        if not email:
            return False, " ."
        
        if len(email) > 254:  # RFC 5321 
            return False, "  . ( 254)"
        
        #   
        if not cls.EMAIL_REGEX.match(email):
            return False, "   ."
        
        #   
        local_part, domain = email.rsplit('@', 1)
        
        #     (RFC 5321)
        if len(local_part) > 64:
            return False, "   . ( 64)"
        
        #   
        if '..' in email:
            return False, "   ."
        
        # /  
        if local_part.startswith('.') or local_part.endswith('.'):
            return False, "   ."
        
        # XSS  
        xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', '<iframe']
        for pattern in xss_patterns:
            if pattern.lower() in email.lower():
                return False, "     ."
        
        return True, None
    
    @classmethod
    def validate_password(cls, password):
        """
           (  )
        Returns: (is_valid: bool, error_message: str or None)
        """
        if not password:
            return False, " ."
        
        #  
        if len(password) < cls.PASSWORD_MIN_LENGTH:
            return False, f"  {cls.PASSWORD_MIN_LENGTH}  ."
        
        if len(password) > cls.PASSWORD_MAX_LENGTH:
            return False, f"  {cls.PASSWORD_MAX_LENGTH} ."
        
        #    
        #  1:  + 
        #  2:  + 
        #  3:  + 
        has_letter = bool(re.search(r'[A-Za-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', password))
        
        #  2   OK
        type_count = sum([has_letter, has_digit, has_special])
        
        if type_count < 2:
            if has_letter and not has_digit and not has_special:
                return False, "   ."
            elif has_digit and not has_letter and not has_special:
                return False, "   ."
            else:
                return False, " , ,   2   ."
        
        #     ()
        if password.lower() in ['password', '12345678', 'qwerty', 'admin']:
            return False, "     ."
        
        return True, None
    
    @classmethod
    def validate_text_input(cls, text, field_name, max_length=1000):
        """
           
        Returns: (is_valid: bool, error_message: str or None)
        """
        if not text:
            return False, f"{field_name}() ."
        
        if len(text) > max_length:
            return False, f"{field_name}()  {max_length}  ."
        
        # XSS  
        xss_patterns = [
            '<script', '</script>', 'javascript:', 'onload=', 'onerror=', 
            '<iframe', 'eval(', 'alert(', 'document.cookie'
        ]
        for pattern in xss_patterns:
            if pattern.lower() in text.lower():
                return False, f"{field_name}     ."
        
        return True, None


def validate_request_data(required_fields=None, optional_fields=None):
    """
       
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            try:
                import json
                if request.method in ['POST', 'PUT', 'PATCH']:
                    data = json.loads(request.body)
                elif request.method == 'GET':
                    data = request.GET.dict()
                else:
                    data = {}
                
                #   
                if required_fields:
                    for field in required_fields:
                        if field not in data or not data[field]:
                            return JsonResponse({
                                'error': f'{field}  .',
                                'code': 'MISSING_REQUIRED_FIELD'
                            }, status=400)
                
                #   
                if 'email' in data:
                    is_valid, error_msg = InputValidator.validate_email(data['email'])
                    if not is_valid:
                        return JsonResponse({
                            'error': error_msg,
                            'code': 'INVALID_EMAIL'
                        }, status=400)
                
                #   
                if 'password' in data:
                    is_valid, error_msg = InputValidator.validate_password(data['password'])
                    if not is_valid:
                        return JsonResponse({
                            'error': error_msg,
                            'code': 'INVALID_PASSWORD'
                        }, status=400)
                
                return view_func(request, *args, **kwargs)
                
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': ' JSON .',
                    'code': 'INVALID_JSON'
                }, status=400)
            except Exception as e:
                logger.error(f"Request validation error: {str(e)}")
                return JsonResponse({
                    'error': '    .',
                    'code': 'VALIDATION_ERROR'
                }, status=400)
        
        return wrapper
    return decorator


class FileValidator:
    """   """
    
    #   
    ALLOWED_EXTENSIONS = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
        'document': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'],
        'audio': ['mp3', 'wav', 'ogg', 'm4a', 'aac'],
    }
    
    # MIME  
    MIME_TYPE_MAPPING = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'pdf': 'application/pdf',
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
    }
    
    #    ()
    MAX_FILE_SIZES = {
        'image': 10 * 1024 * 1024,  # 10MB
        'video': 500 * 1024 * 1024,  # 500MB
        'document': 50 * 1024 * 1024,  # 50MB
        'audio': 50 * 1024 * 1024,  # 50MB
    }
    
    @classmethod
    def validate_file(cls, file, file_type='image'):
        """
         
        Returns: (is_valid: bool, error_message: str or None)
        """
        if not file:
            return False, " ."
        
        #   
        filename = file.name
        if not filename:
            return False, "  ."
        
        #    
        if len(filename) > 255:
            return False, "   ."
        
        #     
        dangerous_chars = ['..', '/', '\\', '\x00', '%00']
        for char in dangerous_chars:
            if char in filename:
                return False, "      ."
        
        #  
        ext = filename.split('.')[-1].lower()
        allowed_exts = cls.ALLOWED_EXTENSIONS.get(file_type, [])
        if ext not in allowed_exts:
            return False, f"   .  : {', '.join(allowed_exts)}"
        
        #   
        max_size = cls.MAX_FILE_SIZES.get(file_type, 10 * 1024 * 1024)
        if file.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"   .  {max_size_mb}MB ."
        
        # MIME   (magic   )
        try:
            import magic
            #   MIME  
            mime = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)  #   
            
            expected_mime = cls.MIME_TYPE_MAPPING.get(ext)
            if expected_mime and mime != expected_mime:
                return False, "    ."
        except ImportError:
            # magic      
            pass
        except Exception as e:
            logger.warning(f"MIME type validation error: {str(e)}")
        
        #    (  )
        try:
            file.seek(0)
            content_sample = file.read(1024)  #  1KB 
            file.seek(0)
            
            #    
            executable_signatures = [
                b'MZ',  # Windows PE
                b'\x7fELF',  # Linux ELF
                b'\xca\xfe\xba\xbe',  # Mach-O
                b'\xfe\xed\xfa',  # Mach-O
                b'#!/bin/',  # Shell script
                b'#!/usr/bin/',  # Shell script
            ]
            
            for sig in executable_signatures:
                if content_sample.startswith(sig):
                    return False, "    ."
            
            # PHP  
            if b'<?php' in content_sample.lower():
                return False, "PHP      ."
            
        except Exception as e:
            logger.warning(f"File content validation error: {str(e)}")
        
        return True, None
    
    @classmethod
    def sanitize_filename(cls, filename):
        """  """
        import string
        import random
        
        #  
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        
        #   
        safe_chars = string.ascii_letters + string.digits + '-_'
        safe_name = ''.join(c if c in safe_chars else '_' for c in name)
        
        #       
        if not safe_name:
            safe_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        #  
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        
        #   ( )
        import time
        timestamp = str(int(time.time()))
        
        return f"{safe_name}_{timestamp}.{ext}" if ext else f"{safe_name}_{timestamp}"