"""
Rate Limiting 
     
"""
import time
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import ipaddress
import json


class RateLimitMiddleware:
    """
    IP  Rate Limiting 
    - /  
    -   
    -     
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate Limiting  
        self.enabled = getattr(settings, 'RATE_LIMITING_ENABLED', not settings.DEBUG)
        
        # IP  
        self.whitelist_ips = set(getattr(settings, 'RATE_LIMIT_WHITELIST_IPS', ['127.0.0.1', '::1']))
        
        #   
        self.test_accounts = set(getattr(settings, 'RATE_LIMIT_TEST_ACCOUNTS', []))
        
        # Rate limit  (  )
        if settings.DEBUG:
            #  :   
            self.endpoints = {
                '/api/users/login/': {'limit': 100, 'window': 60},  # 1 100
                '/api/users/register/': {'limit': 50, 'window': 60},  # 1 50
                '/api/users/password-reset/': {'limit': 20, 'window': 300},  # 5 20
                '/api/users/social-login/': {'limit': 100, 'window': 60},  # 1 100
            }
        else:
            #  :  
            self.endpoints = {
                '/api/users/login/': {'limit': 5, 'window': 300},  # 5 5
                '/api/users/register/': {'limit': 3, 'window': 600},  # 10 3
                '/api/users/password-reset/': {'limit': 3, 'window': 3600},  # 1 3
                '/api/users/social-login/': {'limit': 10, 'window': 300},  # 5 10
            }
    
    def __call__(self, request):
        # Rate Limiting    
        if not self.enabled:
            return self.get_response(request)
            
        #  IP 
        client_ip = self.get_client_ip(request)
        if self.is_whitelisted_ip(client_ip):
            return self.get_response(request)
            
        #    (  )
        if self.is_test_account_request(request):
            return self.get_response(request)
        
        # Rate limiting 
        for endpoint, config in self.endpoints.items():
            if request.path.startswith(endpoint):
                if not self.check_rate_limit(request, endpoint, config):
                    return JsonResponse({
                        'error': '  .    .',
                        'retry_after': config['window'],
                        'debug_info': {
                            'ip': client_ip,
                            'endpoint': endpoint,
                            'limit': config['limit'],
                            'window': config['window']
                        } if settings.DEBUG else None
                    }, status=429)
        
        response = self.get_response(request)
        return response
    
    def is_whitelisted_ip(self, ip):
        """IP   """
        if not ip:
            return False
            
        #  
        if ip in self.whitelist_ips:
            return True
            
        # CIDR   (: 192.168.0.0/24)
        try:
            ip_obj = ipaddress.ip_address(ip)
            for whitelist_entry in self.whitelist_ips:
                try:
                    if '/' in whitelist_entry:
                        network = ipaddress.ip_network(whitelist_entry, strict=False)
                        if ip_obj in network:
                            return True
                except (ValueError, ipaddress.AddressValueError):
                    continue
        except (ValueError, ipaddress.AddressValueError):
            pass
            
        return False
        
    def is_test_account_request(self, request):
        """   """
        if not self.test_accounts or request.path != '/api/users/login/':
            return False
            
        try:
            if request.body:
                data = json.loads(request.body)
                email = data.get('email', '')
                return email in self.test_accounts
        except (json.JSONDecodeError, AttributeError):
            pass
            
        return False
    
    def check_rate_limit(self, request, endpoint, config):
        """Rate limit """
        ip = self.get_client_ip(request)
        cache_key = f'rate_limit:{endpoint}:{ip}'
        
        #      
        requests = cache.get(cache_key, [])
        now = time.time()
        
        #   
        requests = [req_time for req_time in requests if now - req_time < config['window']]
        
        #   
        if len(requests) >= config['limit']:
            return False
        
        #   
        requests.append(now)
        cache.set(cache_key, requests, config['window'])
        
        return True
    
    def get_client_ip(self, request):
        """ IP  """
        # Railway, Vercel     IP 
        forwarded_ips = [
            request.META.get('HTTP_X_FORWARDED_FOR'),
            request.META.get('HTTP_X_REAL_IP'),
            request.META.get('HTTP_CF_CONNECTING_IP'),  # Cloudflare
            request.META.get('HTTP_X_FORWARDED'),
            request.META.get('HTTP_FORWARDED_FOR'),
            request.META.get('HTTP_FORWARDED')
        ]
        
        for forwarded in forwarded_ips:
            if forwarded:
                #   IP   IP
                ip = forwarded.split(',')[0].strip()
                if ip and ip != 'unknown':
                    return ip
                    
        return request.META.get('REMOTE_ADDR', 'unknown')


class SecurityAuditMiddleware:
    """
       
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            'script>',
            'javascript:',
            'onerror=',
            'onload=',
            'SELECT * FROM',
            'DROP TABLE',
            'UNION SELECT',
            '../../',
            '%00',
            '\x00',
        ]
    
    def __call__(self, request):
        #   
        self.check_suspicious_activity(request)
        
        response = self.get_response(request)
        
        #    
        if request.path.startswith('/api/users/login/') and response.status_code == 401:
            self.log_failed_login(request)
        
        return response
    
    def check_suspicious_activity(self, request):
        """  """
        # GET  
        for param, value in request.GET.items():
            if isinstance(value, str):
                for pattern in self.suspicious_patterns:
                    if pattern.lower() in value.lower():
                        self.log_security_event('SUSPICIOUS_REQUEST', request, f'Pattern: {pattern}')
                        break
        
        # POST   (JSON)
        if request.content_type == 'application/json' and request.body:
            try:
                import json
                data = json.loads(request.body)
                self.check_dict_for_patterns(data, request)
            except:
                pass
    
    def check_dict_for_patterns(self, data, request, path=''):
        """  """
        if isinstance(data, dict):
            for key, value in data.items():
                self.check_dict_for_patterns(value, request, f'{path}.{key}')
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self.check_dict_for_patterns(item, request, f'{path}[{i}]')
        elif isinstance(data, str):
            for pattern in self.suspicious_patterns:
                if pattern.lower() in data.lower():
                    self.log_security_event('SUSPICIOUS_INPUT', request, f'Path: {path}, Pattern: {pattern}')
                    break
    
    def log_failed_login(self, request):
        """   """
        ip = self.get_client_ip(request)
        try:
            import json
            data = json.loads(request.body) if request.body else {}
            email = data.get('email', 'unknown')
        except:
            email = 'unknown'
        
        self.log_security_event('FAILED_LOGIN', request, f'Email: {email}, IP: {ip}')
    
    def log_security_event(self, event_type, request, details):
        """  """
        import logging
        logger = logging.getLogger('security')
        
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        
        logger.warning(
            f"SECURITY_EVENT: {event_type} | "
            f"Path: {request.path} | "
            f"Method: {request.method} | "
            f"IP: {ip} | "
            f"User-Agent: {user_agent} | "
            f"Details: {details}"
        )
    
    def get_client_ip(self, request):
        """ IP  """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip