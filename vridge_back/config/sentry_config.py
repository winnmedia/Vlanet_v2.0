"""
Sentry  
     
"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
import os

def init_sentry():
    """Sentry """
    
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    ENVIRONMENT = os.environ.get('DJANGO_ENV', 'development')
    
    if not SENTRY_DSN:
        logging.warning("Sentry DSN not configured. Monitoring disabled.")
        return
    
    #   
    logging_integration = LoggingIntegration(
        level=logging.INFO,        # INFO   
        event_level=logging.ERROR   # ERROR   
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='endpoint',
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            RedisIntegration(),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
            logging_integration,
        ],
        
        #  
        traces_sample_rate=0.1 if ENVIRONMENT == 'production' else 1.0,
        profiles_sample_rate=0.1 if ENVIRONMENT == 'production' else 1.0,
        
        #  
        environment=ENVIRONMENT,
        release=os.environ.get('RAILWAY_GIT_COMMIT_SHA', 'unknown'),
        
        #  
        before_send=before_send_filter,
        before_send_transaction=before_send_transaction_filter,
        
        #  
        attach_stacktrace=True,
        send_default_pii=False,  # PII   
        
        #  
        ignore_errors=[
            'DisallowedHost',
            'Http404',
            'PermissionDenied',
            'SuspiciousOperation',
        ],
        
        #  
        max_breadcrumbs=50,
        
        #  
        auto_session_tracking=True,
    )

def before_send_filter(event, hint):
    """
       
          
    """
    
    #    
    if os.environ.get('DJANGO_ENV') == 'development':
        logging.error(f"Sentry Event: {event.get('message', 'No message')}")
    
    #   
    if 'request' in event:
        request = event['request']
        
        #    
        if 'headers' in request:
            sensitive_headers = ['Authorization', 'Cookie', 'X-CSRFToken']
            for header in sensitive_headers:
                if header in request['headers']:
                    request['headers'][header] = '[REDACTED]'
        
        #   
        if 'cookies' in request:
            request['cookies'] = '[REDACTED]'
        
        # POST   
        if 'data' in request:
            if isinstance(request['data'], dict):
                for key in ['password', 'password1', 'password2', 'token', 'secret']:
                    if key in request['data']:
                        request['data'][key] = '[REDACTED]'
    
    #  URL  
    if 'request' in event and 'url' in event['request']:
        ignored_paths = ['/health/', '/api/health/', '/admin/jsi18n/']
        for path in ignored_paths:
            if path in event['request']['url']:
                return None
    
    #    
    if 'tags' in event and event['tags'].get('test') == 'true':
        return None
    
    return event

def before_send_transaction_filter(event, hint):
    """
      
       
    """
    
    #   
    if event.get('transaction') in ['/health/', '/api/health/']:
        return None
    
    #    
    if event.get('transaction', '').startswith('/static/'):
        return None
    
    #    
    if event.get('transaction', '').startswith('/media/'):
        return None
    
    return event

def capture_message(message, level='info', **kwargs):
    """
       
    """
    extra_context = kwargs.get('extra', {})
    tags = kwargs.get('tags', {})
    
    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)
        for key, value in tags.items():
            scope.set_tag(key, value)
        
        sentry_sdk.capture_message(message, level=level)

def capture_exception(exception, **kwargs):
    """
       
    """
    extra_context = kwargs.get('extra', {})
    tags = kwargs.get('tags', {})
    
    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)
        for key, value in tags.items():
            scope.set_tag(key, value)
        
        sentry_sdk.capture_exception(exception)

#   
def monitor_performance(op_name):
    """
       
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with sentry_sdk.start_span(op=op_name) as span:
                span.set_tag('function', func.__name__)
                try:
                    result = func(*args, **kwargs)
                    span.set_status('ok')
                    return result
                except Exception as e:
                    span.set_status('error')
                    span.set_tag('error', str(e))
                    raise
        return wrapper
    return decorator