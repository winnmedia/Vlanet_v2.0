"""
  
      
"""
import hashlib
import json
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class IdempotencyMiddleware(MiddlewareMixin):
    """
          
    """
    
    def process_request(self, request):
        # POST, PUT, PATCH   
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return None
        
        #    
        if not request.path.startswith('/api/projects/'):
            return None
        
        #   
        idempotency_key = request.headers.get('X-Idempotency-Key')
        if not idempotency_key:
            #      
            try:
                body = request.body.decode('utf-8')
                if body:
                    #  ID     
                    user_id = getattr(request.user, 'id', 'anonymous')
                    hash_input = f"{user_id}:{request.path}:{body}"
                    idempotency_key = hashlib.sha256(hash_input.encode()).hexdigest()
            except:
                return None
        
        if idempotency_key:
            cache_key = f"idempotency:{idempotency_key}"
            
            #    
            in_progress = cache.get(f"{cache_key}:progress")
            if in_progress:
                return JsonResponse({
                    "message": "    .    .",
                    "code": "REQUEST_IN_PROGRESS"
                }, status=409)
            
            #    
            cached_response = cache.get(cache_key)
            if cached_response:
                return JsonResponse(cached_response['data'], status=cached_response['status'])
            
            #    
            cache.set(f"{cache_key}:progress", True, timeout=30)  # 30 
            
            #     
            request.idempotency_key = idempotency_key
            request.idempotency_cache_key = cache_key
    
    def process_response(self, request, response):
        #      
        if hasattr(request, 'idempotency_cache_key') and response.status_code < 500:
            cache_key = request.idempotency_cache_key
            
            #    
            cache.delete(f"{cache_key}:progress")
            
            #    (2xx, 3xx)
            if 200 <= response.status_code < 400:
                try:
                    response_data = {
                        'data': json.loads(response.content),
                        'status': response.status_code
                    }
                    # 1  
                    cache.set(cache_key, response_data, timeout=3600)
                except:
                    pass
        
        return response
    
    def process_exception(self, request, exception):
        #       
        if hasattr(request, 'idempotency_cache_key'):
            cache_key = request.idempotency_cache_key
            cache.delete(f"{cache_key}:progress")