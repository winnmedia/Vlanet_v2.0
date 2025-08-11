from django.utils.deprecation import MiddlewareMixin
import mimetypes
from urllib.parse import unquote
from django.http import HttpResponseNotFound
import os
from django.conf import settings

class MediaHeadersMiddleware(MiddlewareMixin):
    """     """
    
    def process_request(self, request):
        """   """
        if request.path.startswith('/media/'):
            import logging
            logger = logging.getLogger(__name__)
            
            # URL 
            decoded_path = unquote(request.path)
            logger.info(f"Media request - Original path: {request.path}")
            logger.info(f"Media request - Decoded path: {decoded_path}")
            
            #    
            relative_path = decoded_path.replace('/media/', '')
            file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            
            #    
            if not os.path.exists(file_path):
                logger.warning(f"File not found at: {file_path}")
                
                #   
                encoded_path = request.path.replace('/media/', '')
                encoded_file_path = os.path.join(settings.MEDIA_ROOT, encoded_path)
                
                if os.path.exists(encoded_file_path):
                    logger.info(f"Found file at encoded path: {encoded_file_path}")
                    #      
                else:
                    #      
                    try:
                        dir_path = os.path.dirname(file_path)
                        if os.path.exists(dir_path):
                            files_in_dir = os.listdir(dir_path)
                            logger.info(f"Files in directory {dir_path}: {files_in_dir[:5]}")  #  5
                    except Exception as e:
                        logger.error(f"Error listing directory: {e}")
                    
                    return HttpResponseNotFound('File not found')
    
    def process_response(self, request, response):
        if request.path.startswith('/media/'):
            # Content-Type 
            content_type, _ = mimetypes.guess_type(request.path)
            if content_type:
                response['Content-Type'] = content_type
            
            # CORS   - settings.py CORS_ALLOWED_ORIGINS 
            origin = request.headers.get('Origin', '')
            allowed_origins = [
                'https://vlanet.net',
                'https://www.vlanet.net',
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'https://vlanet-v1-0.vercel.app',
                'https://videoplanet.up.railway.app',
                'https://api.vlanet.net',
            ]
            
            # Origin     Origin ,  vlanet.net 
            if origin in allowed_origins:
                response['Access-Control-Allow-Origin'] = origin
            else:
                response['Access-Control-Allow-Origin'] = 'https://vlanet.net'
            
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS, HEAD'
            response['Access-Control-Allow-Headers'] = 'Range, Content-Type, Accept, Origin'
            response['Access-Control-Allow-Credentials'] = 'true'
            
            #     
            if any(request.path.endswith(ext) for ext in ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']):
                response['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, Accept-Ranges'
                response['Accept-Ranges'] = 'bytes'
                response['Cache-Control'] = 'public, max-age=3600'
            else:
                #     
                response['Cache-Control'] = 'public, max-age=86400'  # 24
                
        return response