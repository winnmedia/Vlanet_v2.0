"""
   
Railway    
"""
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_http_methods
import mimetypes

@require_http_methods(["GET", "HEAD"])
@cache_control(max_age=86400)  # 24 
def serve_media(request, path):
    """
        
    Range     
    """
    # : path traversal 
    if '..' in path or path.startswith('/'):
        raise Http404("Invalid path")
    
    #   
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    #   
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("File not found")
    
    # MIME  
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'
    
    #  
    file_size = os.path.getsize(file_path)
    
    # Range  
    range_header = request.META.get('HTTP_RANGE', None)
    if range_header:
        import re
        from django.http import HttpResponse
        
        # Range   (: "bytes=1048576-")
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            
            #   
            if start >= file_size:
                return HttpResponse(status=416)  # Range Not Satisfiable
            
            end = min(end, file_size - 1)
            length = end - start + 1
            
            #     
            file_handle = open(file_path, 'rb')
            file_handle.seek(start)
            
            #   
            response = HttpResponse(
                file_handle.read(length),
                status=206,  # Partial Content
                content_type=content_type
            )
            
            # Range   
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Content-Length'] = str(length)
            response['Accept-Ranges'] = 'bytes'
            
            # CORS  
            # Origin      CORS 
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
            
            if origin in allowed_origins:
                response['Access-Control-Allow-Origin'] = origin
            else:
                response['Access-Control-Allow-Origin'] = 'https://vlanet.net'
            
            response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Range, Content-Type, Accept, Origin'
            response['Access-Control-Expose-Headers'] = 'Content-Range, Accept-Ranges, Content-Length'
            response['Access-Control-Allow-Credentials'] = 'true'
            
            return response
    
    # Range      
    response = FileResponse(
        open(file_path, 'rb'),
        content_type=content_type
    )
    
    #  
    filename = os.path.basename(file_path)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    response['Content-Length'] = str(file_size)
    
    #    Range   
    if content_type.startswith('video/'):
        response['Accept-Ranges'] = 'bytes'
    
    # CORS  
    # Origin      CORS 
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
    
    if origin in allowed_origins:
        response['Access-Control-Allow-Origin'] = origin
    else:
        #    
        response['Access-Control-Allow-Origin'] = 'https://vlanet.net'
    
    response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Range, Content-Type, Accept, Origin'
    response['Access-Control-Allow-Credentials'] = 'true'
    
    return response