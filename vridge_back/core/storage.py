"""
   
-   S3   
-   
-  
"""

import os
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class MediaStorage(FileSystemStorage):
    """
      
    -   
    -   
    -   
    """
    
    def __init__(self, *args, **kwargs):
        if settings.USE_S3:
            # S3  
            from storages.backends.s3boto3 import S3Boto3Storage
            self.__class__ = type('S3MediaStorage', (S3Boto3Storage,), {
                'bucket_name': settings.AWS_STORAGE_BUCKET_NAME,
                'custom_domain': settings.AWS_S3_CUSTOM_DOMAIN,
                'object_parameters': settings.AWS_S3_OBJECT_PARAMETERS,
                'file_overwrite': False,
                'default_acl': 'private',  #  
                'querystring_auth': True,  #  URL 
                'querystring_expire': 3600,  # 1
            })
            return S3Boto3Storage.__init__(self)
        else:
            #   
            super().__init__(*args, **kwargs)
            self.base_location = settings.MEDIA_ROOT
            self.base_url = settings.MEDIA_URL
    
    def get_valid_name(self, name):
        """
          
        -    
        -  
        """
        import unicodedata
        import re
        
        #   
        name = Path(name).name
        stem = Path(name).stem
        suffix = Path(name).suffix
        
        #     
        if any(ord(char) > 127 for char in stem):
            #    
            hash_object = hashlib.md5(stem.encode('utf-8'))
            stem = hash_object.hexdigest()[:8]
        
        # , , ,  
        stem = re.sub(r'[^a-zA-Z0-9_-]', '_', stem)
        
        #    
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{stem}_{timestamp}{suffix}"
    
    def get_available_name(self, name, max_length=None):
        """
           
        """
        #    
        name = self.get_valid_name(name)
        
        #      
        return super().get_available_name(name, max_length)
    
    def _save(self, name, content):
        """
            
        """
        # MIME  
        if hasattr(content, 'content_type'):
            content_type = content.content_type
        else:
            content_type = mimetypes.guess_type(name)[0]
        
        #    
        allowed_types = getattr(settings, 'ALLOWED_UPLOAD_TYPES', {
            'video': ['video/mp4', 'video/quicktime', 'video/x-msvideo', 
                     'video/x-ms-wmv', 'video/x-matroska'],
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'document': ['application/pdf', 'application/msword',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        })
        
        #     
        file_category = None
        for category, types in allowed_types.items():
            if content_type in types:
                file_category = category
                break
        
        if not file_category:
            #     
            file_category = 'misc'
        
        # /   
        date_path = datetime.now().strftime('%Y/%m')
        name = os.path.join(file_category, date_path, name)
        
        return super()._save(name, content)


class StaticStorage(FileSystemStorage):
    """
      
     WhiteNoise  
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_location = settings.STATIC_ROOT
        self.base_url = settings.STATIC_URL


def clean_filename(filename):
    """
       
    """
    import re
    
    #   
    name, ext = os.path.splitext(filename)
    
    #   
    name = re.sub(r'[^\w\s-]', '_', name)
    
    #   
    name = re.sub(r'\s+', '_', name)
    
    #   
    name = re.sub(r'_+', '_', name)
    
    #   
    name = name.strip('_')
    
    #    
    if not name:
        name = 'file'
    
    return f"{name}{ext}"


def get_upload_path(instance, filename):
    """
       
    """
    #   
    model_name = instance.__class__.__name__.lower()
    
    #   
    date_path = datetime.now().strftime('%Y/%m/%d')
    
    #  
    safe_filename = clean_filename(filename)
    
    #   (user   )
    if hasattr(instance, 'user') and instance.user:
        user_path = f"user_{instance.user.id}"
        return os.path.join(model_name, user_path, date_path, safe_filename)
    
    return os.path.join(model_name, date_path, safe_filename)


#  
media_storage = MediaStorage()


# S3 presigned URL  
def generate_presigned_url(file_path, expires_in=3600):
    """
    S3 presigned URL 
    -    
    -  
    """
    if not settings.USE_S3:
        #    URL 
        return settings.MEDIA_URL + file_path
    
    try:
        from boto3 import client
        
        s3_client = client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_path,
            },
            ExpiresIn=expires_in
        )
        
        return url
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Presigned URL  : {e}")
        return None