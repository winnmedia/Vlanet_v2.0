import logging
import time
import json
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class DetailedLoggingMiddleware:
    """
           
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #    
        start_time = time.time()
        
        #   
        self._log_request(request)
        
        #     
        response = self.get_response(request)
        
        #   
        duration = time.time() - start_time
        self._log_response(request, response, duration)
        
        return response
    
    def _log_request(self, request):
        """  """
        log_data = {
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        # POST   (  )
        if request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    body = json.loads(request.body)
                    #     
                    if isinstance(body, dict):
                        safe_body = {k: '***' if 'password' in k.lower() else v 
                                   for k, v in body.items()}
                        log_data['body'] = safe_body
                else:
                    log_data['body_keys'] = list(request.POST.keys())
            except:
                log_data['body'] = 'Could not parse body'
        
        logger.info(f"REQUEST: {json.dumps(log_data, indent=2)}")
    
    def _log_response(self, request, response, duration):
        """  """
        log_data = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
        }
        
        #       
        if response.status_code >= 400:
            if hasattr(response, 'content'):
                try:
                    content = response.content.decode('utf-8')
                    if len(content) < 1000:  #    
                        log_data['response_body'] = content
                except:
                    pass
        
        log_level = logging.ERROR if response.status_code >= 500 else \
                   logging.WARNING if response.status_code >= 400 else \
                   logging.INFO
        
        logger.log(log_level, f"RESPONSE: {json.dumps(log_data, indent=2)}")
    
    def _get_client_ip(self, request):
        """ IP  """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def process_exception(self, request, exception):
        """    """
        logger.error(
            f"EXCEPTION in {request.method} {request.path}: "
            f"{type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            }
        )
        return None