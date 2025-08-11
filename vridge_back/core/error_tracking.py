"""
     
" ,  "       
"""
import logging
import traceback
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.core.mail import send_mail
from django.http import JsonResponse

logger = logging.getLogger('error_tracking')

class ErrorSeverity(Enum):
    """ """
    LOW = "low"           # , 
    MEDIUM = "medium"     # ,  
    HIGH = "high"         # ,   
    CRITICAL = "critical" # ,   

class ErrorCategory(Enum):
    """ """
    SYSTEM = "system"           #  
    DATABASE = "database"       #  
    API = "api"                # API  
    VALIDATION = "validation"   #   
    PERMISSION = "permission"   #  
    BUSINESS_LOGIC = "business" #   
    EXTERNAL_SERVICE = "external" #   
    USER = "user"              #   

@dataclass
class ErrorContext:
    """  """
    user_id: Optional[int] = None
    username: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    request_data: Optional[Dict] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    planning_id: Optional[int] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorRecord:
    """ """
    error_id: str
    timestamp: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    stack_trace: str
    context: ErrorContext
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_method: Optional[str] = None
    occurrence_count: int = 1
    first_occurrence: Optional[str] = None
    last_occurrence: Optional[str] = None

class AutoRecoveryStrategy:
    """  """
    
    def __init__(self, name: str, condition: Callable, action: Callable, max_attempts: int = 3):
        self.name = name
        self.condition = condition  #   
        self.action = action       #   
        self.max_attempts = max_attempts
        self.attempt_count = 0
    
    def can_recover(self, error_record: ErrorRecord) -> bool:
        """   """
        return self.condition(error_record) and self.attempt_count < self.max_attempts
    
    def attempt_recovery(self, error_record: ErrorRecord) -> bool:
        """ """
        self.attempt_count += 1
        try:
            return self.action(error_record)
        except Exception as e:
            logger.error(f"  '{self.name}'  : {str(e)}")
            return False

class ErrorTrackingSystem:
    """  """
    
    def __init__(self):
        self.recovery_strategies: List[AutoRecoveryStrategy] = []
        self.error_patterns: Dict[str, List[ErrorRecord]] = {}
        self.alert_thresholds = {
            ErrorSeverity.LOW: 100,      # 100 
            ErrorSeverity.MEDIUM: 50,    # 50 
            ErrorSeverity.HIGH: 10,      # 10 
            ErrorSeverity.CRITICAL: 1,   # 
        }
        self._initialize_recovery_strategies()
    
    def _initialize_recovery_strategies(self):
        """   """
        
        #    
        self.add_recovery_strategy(AutoRecoveryStrategy(
            name="database_reconnect",
            condition=lambda error: error.category == ErrorCategory.DATABASE and "connection" in error.message.lower(),
            action=self._recover_database_connection,
            max_attempts=3
        ))
        
        # API   
        self.add_recovery_strategy(AutoRecoveryStrategy(
            name="api_retry",
            condition=lambda error: error.category == ErrorCategory.API and ("timeout" in error.message.lower() or "connection" in error.message.lower()),
            action=self._recover_api_call,
            max_attempts=3
        ))
        
        #   
        self.add_recovery_strategy(AutoRecoveryStrategy(
            name="cache_fallback",
            condition=lambda error: "cache" in error.message.lower() or "redis" in error.message.lower(),
            action=self._recover_cache_error,
            max_attempts=2
        ))
        
        #    
        self.add_recovery_strategy(AutoRecoveryStrategy(
            name="filesystem_recovery",
            condition=lambda error: "permission denied" in error.message.lower() or "no such file" in error.message.lower(),
            action=self._recover_filesystem_error,
            max_attempts=2
        ))
        
        #    
        self.add_recovery_strategy(AutoRecoveryStrategy(
            name="memory_cleanup",
            condition=lambda error: "memory" in error.message.lower() or "out of memory" in error.message.lower(),
            action=self._recover_memory_error,
            max_attempts=1
        ))
    
    def add_recovery_strategy(self, strategy: AutoRecoveryStrategy):
        """  """
        self.recovery_strategies.append(strategy)
    
    def track_error(self, 
                   exception: Exception, 
                   severity: ErrorSeverity,
                   category: ErrorCategory,
                   context: ErrorContext,
                   custom_message: Optional[str] = None) -> ErrorRecord:
        """ """
        
        #   
        error_id = self._generate_error_id(exception, context)
        
        error_record = ErrorRecord(
            error_id=error_id,
            timestamp=timezone.now().isoformat(),
            severity=severity,
            category=category,
            message=custom_message or str(exception),
            exception_type=type(exception).__name__,
            stack_trace=traceback.format_exc(),
            context=context
        )
        
        #    
        pattern_key = self._get_error_pattern_key(error_record)
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = []
            error_record.first_occurrence = error_record.timestamp
        else:
            #    
            existing_errors = self.error_patterns[pattern_key]
            error_record.occurrence_count = len(existing_errors) + 1
            error_record.first_occurrence = existing_errors[0].timestamp
        
        error_record.last_occurrence = error_record.timestamp
        self.error_patterns[pattern_key].append(error_record)
        
        #  
        self._log_error(error_record)
        
        #   
        if self._should_attempt_recovery(error_record):
            recovery_success = self._attempt_auto_recovery(error_record)
            error_record.recovery_attempted = True
            error_record.recovery_successful = recovery_success
        
        #    
        if self._should_send_alert(error_record):
            self._send_alert(error_record)
        
        #     (24)
        cache.set(f"error:{error_id}", error_record, 86400)
        
        return error_record
    
    def _generate_error_id(self, exception: Exception, context: ErrorContext) -> str:
        """ ID """
        import hashlib
        
        #  , ,    
        error_signature = f"{type(exception).__name__}:{str(exception)}:{context.request_path}"
        
        return hashlib.md5(error_signature.encode()).hexdigest()[:12]
    
    def _get_error_pattern_key(self, error_record: ErrorRecord) -> str:
        """   """
        return f"{error_record.category.value}:{error_record.exception_type}:{hash(error_record.message[:100])}"
    
    def _log_error(self, error_record: ErrorRecord):
        """ """
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[error_record.severity]
        
        log_message = (
            f"[{error_record.error_id}] {error_record.category.value.upper()} ERROR: "
            f"{error_record.message} "
            f"(User: {error_record.context.username or 'Anonymous'}, "
            f"Path: {error_record.context.request_path or 'N/A'})"
        )
        
        logger.log(log_level, log_message)
        
        #      
        if error_record.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            critical_logger = logging.getLogger('critical_errors')
            critical_logger.error(f"{log_message}\n{error_record.stack_trace}")
    
    def _should_attempt_recovery(self, error_record: ErrorRecord) -> bool:
        """    """
        #       
        if error_record.severity == ErrorSeverity.CRITICAL:
            return False
        
        if error_record.category == ErrorCategory.USER:
            return False
        
        #     
        for strategy in self.recovery_strategies:
            if strategy.can_recover(error_record):
                return True
        
        return False
    
    def _attempt_auto_recovery(self, error_record: ErrorRecord) -> bool:
        """  """
        for strategy in self.recovery_strategies:
            if strategy.can_recover(error_record):
                logger.info(f"  '{strategy.name}'  ... ( ID: {error_record.error_id})")
                
                if strategy.attempt_recovery(error_record):
                    error_record.recovery_method = strategy.name
                    logger.info(f"  '{strategy.name}'  ( ID: {error_record.error_id})")
                    return True
                else:
                    logger.warning(f"  '{strategy.name}'  ( ID: {error_record.error_id})")
        
        return False
    
    def _should_send_alert(self, error_record: ErrorRecord) -> bool:
        """   """
        threshold = self.alert_thresholds.get(error_record.severity, 1)
        return error_record.occurrence_count >= threshold
    
    def _send_alert(self, error_record: ErrorRecord):
        """ """
        try:
            #    
            if settings.DEBUG:
                print(f" ERROR ALERT: {error_record.message}")
                return
            
            #   ( )
            subject = f"VideoPlanet Error Alert - {error_record.severity.value.upper()}"
            message = self._format_alert_message(error_record)
            
            #   
            admin_emails = getattr(settings, 'ADMIN_EMAILS', ['admin@videoplanet.com'])
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=True
            )
            
            # Slack, Discord     ( )
            # self._send_slack_alert(error_record)
            
        except Exception as e:
            logger.error(f"  : {str(e)}")
    
    def _format_alert_message(self, error_record: ErrorRecord) -> str:
        """  """
        return f"""
VideoPlanet   

  :
- ID: {error_record.error_id}
- : {error_record.severity.value.upper()}
- : {error_record.category.value}
-  : {error_record.timestamp}
-  : {error_record.occurrence_count}

  :
{error_record.message}

  :
- : {error_record.context.username or 'Anonymous'}
- IP: {error_record.context.ip_address or 'N/A'}
- : {error_record.context.request_path or 'N/A'}

  :
- : {'' if error_record.recovery_attempted else ''}
- : {'' if error_record.recovery_successful else ''}
- : {error_record.recovery_method or 'N/A'}

 Stack Trace:
{error_record.stack_trace[:500]}...
        """.strip()
    
    #   
    def _recover_database_connection(self, error_record: ErrorRecord) -> bool:
        """  """
        try:
            from django.db import connection
            connection.close()
            
            #  
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            logger.info("   ")
            return True
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return False
    
    def _recover_api_call(self, error_record: ErrorRecord) -> bool:
        """API   ()"""
        try:
            #     ( )
            import time
            import random
            
            wait_time = min(2 ** self.recovery_strategies[1].attempt_count + random.uniform(0, 1), 30)
            time.sleep(wait_time)
            
            logger.info(f"API    {wait_time:.2f}   ")
            return True  #  API    
            
        except Exception as e:
            logger.error(f"API   : {str(e)}")
            return False
    
    def _recover_cache_error(self, error_record: ErrorRecord) -> bool:
        """  """
        try:
            #   
            cache.clear()
            
            #    
            logger.info("  :    ")
            return True
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return False
    
    def _recover_filesystem_error(self, error_record: ErrorRecord) -> bool:
        """   """
        try:
            import os
            
            #   
            if "no such file" in error_record.message.lower():
                #     ( )
                #     
                pass
            
            #    
            if "permission denied" in error_record.message.lower():
                logger.info("   ,   ")
                #    
            
            return True
            
        except Exception as e:
            logger.error(f"    : {str(e)}")
            return False
    
    def _recover_memory_error(self, error_record: ErrorRecord) -> bool:
        """  """
        try:
            import gc
            
            #    
            gc.collect()
            
            #  
            cache.clear()
            
            logger.info("  ")
            return True
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return False
    
    def get_error_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """  """
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        statistics = {
            'total_errors': 0,
            'by_severity': {severity.value: 0 for severity in ErrorSeverity},
            'by_category': {category.value: 0 for category in ErrorCategory},
            'recovery_rate': 0,
            'top_errors': [],
            'error_trend': []
        }
        
        total_recovery_attempts = 0
        successful_recoveries = 0
        
        #  
        pattern_stats = {}
        
        for pattern_key, errors in self.error_patterns.items():
            recent_errors = [
                error for error in errors 
                if timezone.datetime.fromisoformat(error.timestamp.replace('Z', '+00:00')) > cutoff_time
            ]
            
            if not recent_errors:
                continue
            
            statistics['total_errors'] += len(recent_errors)
            
            for error in recent_errors:
                #  
                statistics['by_severity'][error.severity.value] += 1
                
                #  
                statistics['by_category'][error.category.value] += 1
                
                #  
                if error.recovery_attempted:
                    total_recovery_attempts += 1
                    if error.recovery_successful:
                        successful_recoveries += 1
            
            #  
            pattern_stats[pattern_key] = {
                'count': len(recent_errors),
                'message': recent_errors[0].message,
                'category': recent_errors[0].category.value,
                'severity': recent_errors[0].severity.value,
                'first_occurrence': recent_errors[0].first_occurrence,
                'last_occurrence': recent_errors[-1].timestamp
            }
        
        #  
        if total_recovery_attempts > 0:
            statistics['recovery_rate'] = (successful_recoveries / total_recovery_attempts) * 100
        
        #   
        statistics['top_errors'] = sorted(
            pattern_stats.values(),
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        return statistics

#     
error_tracker = ErrorTrackingSystem()

class ErrorTrackingMiddleware:
    """  """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """ """
        try:
            #   
            context = ErrorContext(
                user_id=request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
                username=request.user.username if hasattr(request, 'user') and request.user.is_authenticated else None,
                request_path=request.path,
                request_method=request.method,
                request_data=self._safe_get_request_data(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                ip_address=self._get_client_ip(request),
                session_id=request.session.session_key if hasattr(request, 'session') else None
            )
            
            #     
            severity, category = self._classify_error(exception)
            
            #  
            error_record = error_tracker.track_error(exception, severity, category, context)
            
            #    
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'status': 'error',
                    'message': self._get_user_friendly_message(error_record),
                    'error_id': error_record.error_id,
                    'recovery_attempted': error_record.recovery_attempted,
                    'recovery_successful': error_record.recovery_successful
                }, status=500)
        
        except Exception as middleware_error:
            logger.error(f"   : {str(middleware_error)}")
        
        return None  # Django    
    
    def _safe_get_request_data(self, request) -> Dict:
        """   """
        try:
            data = {}
            
            if hasattr(request, 'GET') and request.GET:
                data['GET'] = dict(request.GET)
            
            if hasattr(request, 'POST') and request.POST:
                data['POST'] = dict(request.POST)
                #   
                for sensitive_field in ['password', 'token', 'secret', 'key']:
                    if sensitive_field in data['POST']:
                        data['POST'][sensitive_field] = '*' * 8
            
            return data
        except:
            return {}
    
    def _get_client_ip(self, request) -> str:
        """ IP  """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _classify_error(self, exception) -> tuple[ErrorSeverity, ErrorCategory]:
        """ """
        exception_type = type(exception).__name__
        exception_message = str(exception).lower()
        
        #  
        if any(keyword in exception_message for keyword in ['critical', 'fatal', 'out of memory']):
            severity = ErrorSeverity.CRITICAL
        elif any(keyword in exception_message for keyword in ['database', 'connection', 'timeout']):
            severity = ErrorSeverity.HIGH
        elif any(keyword in exception_message for keyword in ['permission', 'forbidden', 'unauthorized']):
            severity = ErrorSeverity.MEDIUM
        else:
            severity = ErrorSeverity.LOW
        
        #  
        if 'database' in exception_message or 'sql' in exception_message:
            category = ErrorCategory.DATABASE
        elif 'permission' in exception_message or 'forbidden' in exception_message:
            category = ErrorCategory.PERMISSION
        elif 'api' in exception_message or 'http' in exception_message:
            category = ErrorCategory.API
        elif 'validation' in exception_message or 'invalid' in exception_message:
            category = ErrorCategory.VALIDATION
        elif any(keyword in exception_message for keyword in ['user', 'input', 'form']):
            category = ErrorCategory.USER
        else:
            category = ErrorCategory.SYSTEM
        
        return severity, category
    
    def _get_user_friendly_message(self, error_record: ErrorRecord) -> str:
        """   """
        if error_record.category == ErrorCategory.USER:
            return "    ."
        elif error_record.category == ErrorCategory.PERMISSION:
            return "  .  ."
        elif error_record.category == ErrorCategory.DATABASE:
            return "  .     ."
        elif error_record.recovery_successful:
            return "  .   ."
        else:
            return f" .     . ( ID: {error_record.error_id})"

def track_error_decorator(severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                         category: ErrorCategory = ErrorCategory.SYSTEM):
    """  """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    additional_data={
                        'function': func.__name__,
                        'module': func.__module__,
                        'args': str(args)[:200],
                        'kwargs': str(kwargs)[:200]
                    }
                )
                
                error_tracker.track_error(e, severity, category, context)
                raise  #    
        
        return wrapper
    return decorator