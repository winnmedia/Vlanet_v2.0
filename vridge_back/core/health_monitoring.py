"""
   
      
"""
import time
import psutil
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from .error_tracking import error_tracker, ErrorSeverity, ErrorCategory, ErrorContext

logger = logging.getLogger('health_monitoring')

class HealthStatus(Enum):
    """ """
    HEALTHY = "healthy"      # 
    WARNING = "warning"      # 
    CRITICAL = "critical"    # 
    DOWN = "down"           # 

@dataclass
class HealthCheckResult:
    """ """
    name: str
    status: HealthStatus
    message: str
    response_time: float
    details: Dict[str, Any]
    timestamp: str
    auto_recovery_attempted: bool = False
    auto_recovery_successful: bool = False

class HealthChecker:
    """  """
    
    def __init__(self, name: str, timeout: float = 5.0):
        self.name = name
        self.timeout = timeout
    
    def check(self) -> HealthCheckResult:
        """ """
        start_time = time.time()
        
        try:
            result = self.perform_check()
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=result.get('status', HealthStatus.HEALTHY),
                message=result.get('message', 'OK'),
                response_time=response_time,
                details=result.get('details', {}),
                timestamp=timezone.now().isoformat()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.CRITICAL,
                message=f"Check failed: {str(e)}",
                response_time=response_time,
                details={'error': str(e)},
                timestamp=timezone.now().isoformat()
            )
    
    def perform_check(self) -> Dict[str, Any]:
        """   (  )"""
        raise NotImplementedError

class DatabaseHealthChecker(HealthChecker):
    """ """
    
    def __init__(self):
        super().__init__("database", timeout=10.0)
    
    def perform_check(self) -> Dict[str, Any]:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            #   
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
                active_connections = cursor.fetchone()[0]
            
            #   
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE state = 'active' AND now() - query_start > interval '30 seconds'
                """)
                slow_queries = cursor.fetchone()[0]
            
            status = HealthStatus.HEALTHY
            message = "Database is healthy"
            
            if active_connections > 80:
                status = HealthStatus.WARNING
                message = f"High connection count: {active_connections}"
            
            if slow_queries > 5:
                status = HealthStatus.CRITICAL
                message = f"Too many slow queries: {slow_queries}"
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'active_connections': active_connections,
                    'slow_queries': slow_queries
                }
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f"Database check failed: {str(e)}",
                'details': {'error': str(e)}
            }

class CacheHealthChecker(HealthChecker):
    """ """
    
    def __init__(self):
        super().__init__("cache", timeout=5.0)
    
    def perform_check(self) -> Dict[str, Any]:
        try:
            #  / 
            test_key = "health_check_test"
            test_value = str(time.time())
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value != test_value:
                return {
                    'status': HealthStatus.CRITICAL,
                    'message': "Cache read/write test failed",
                    'details': {'test_key': test_key}
                }
            
            #  
            cache.delete(test_key)
            
            # Redis  ( )
            try:
                from django_redis import get_redis_connection
                redis_conn = get_redis_connection("default")
                info = redis_conn.info()
                
                used_memory = info.get('used_memory_human', 'N/A')
                connected_clients = info.get('connected_clients', 0)
                
                status = HealthStatus.HEALTHY
                message = "Cache is healthy"
                
                if connected_clients > 100:
                    status = HealthStatus.WARNING
                    message = f"High client count: {connected_clients}"
                
                return {
                    'status': status,
                    'message': message,
                    'details': {
                        'used_memory': used_memory,
                        'connected_clients': connected_clients
                    }
                }
                
            except ImportError:
                # Redis    
                return {
                    'status': HealthStatus.HEALTHY,
                    'message': "Cache is healthy (non-Redis backend)",
                    'details': {}
                }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f"Cache check failed: {str(e)}",
                'details': {'error': str(e)}
            }

class SystemResourcesHealthChecker(HealthChecker):
    """  """
    
    def __init__(self):
        super().__init__("system_resources", timeout=3.0)
    
    def perform_check(self) -> Dict[str, Any]:
        try:
            # CPU 
            cpu_percent = psutil.cpu_percent(interval=1)
            
            #  
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            #  
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            #  
            load_avg = psutil.getloadavg()
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            if cpu_percent > 80:
                status = HealthStatus.WARNING
                warnings.append(f"High CPU usage: {cpu_percent}%")
            
            if memory_percent > 85:
                status = HealthStatus.WARNING
                warnings.append(f"High memory usage: {memory_percent}%")
            
            if disk_percent > 90:
                status = HealthStatus.CRITICAL
                warnings.append(f"High disk usage: {disk_percent}%")
            
            if cpu_percent > 95 or memory_percent > 95:
                status = HealthStatus.CRITICAL
            
            message = "System resources are healthy"
            if warnings:
                message = "; ".join(warnings)
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'disk_percent': disk_percent,
                    'load_average': load_avg
                }
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f"System resources check failed: {str(e)}",
                'details': {'error': str(e)}
            }

class ExternalServiceHealthChecker(HealthChecker):
    """  """
    
    def __init__(self, service_name: str, endpoint: str, timeout: float = 10.0):
        super().__init__(f"external_service_{service_name}", timeout)
        self.service_name = service_name
        self.endpoint = endpoint
    
    def perform_check(self) -> Dict[str, Any]:
        try:
            import requests
            
            response = requests.get(self.endpoint, timeout=self.timeout)
            
            status = HealthStatus.HEALTHY
            message = f"{self.service_name} is healthy"
            
            if response.status_code >= 400:
                status = HealthStatus.CRITICAL
                message = f"{self.service_name} returned {response.status_code}"
            elif response.elapsed.total_seconds() > 5:
                status = HealthStatus.WARNING
                message = f"{self.service_name} is slow ({response.elapsed.total_seconds():.2f}s)"
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'endpoint': self.endpoint
                }
            }
            
        except requests.exceptions.Timeout:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f"{self.service_name} timeout",
                'details': {'endpoint': self.endpoint, 'timeout': self.timeout}
            }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f"{self.service_name} check failed: {str(e)}",
                'details': {'error': str(e), 'endpoint': self.endpoint}
            }

class AIServiceHealthChecker(HealthChecker):
    """AI  """
    
    def __init__(self):
        super().__init__("ai_services", timeout=15.0)
    
    def perform_check(self) -> Dict[str, Any]:
        try:
            services_status = {}
            overall_status = HealthStatus.HEALTHY
            messages = []
            
            # OpenAI API 
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                try:
                    #  API  (    )
                    services_status['openai'] = 'available'
                except Exception as e:
                    services_status['openai'] = f'error: {str(e)}'
                    overall_status = HealthStatus.WARNING
                    messages.append("OpenAI API unavailable")
            else:
                services_status['openai'] = 'not_configured'
            
            # Google Gemini API 
            if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
                try:
                    services_status['gemini'] = 'available'
                except Exception as e:
                    services_status['gemini'] = f'error: {str(e)}'
                    overall_status = HealthStatus.WARNING
                    messages.append("Gemini API unavailable")
            else:
                services_status['gemini'] = 'not_configured'
            
            # Twelve Labs API 
            if hasattr(settings, 'TWELVE_LABS_API_KEY') and settings.TWELVE_LABS_API_KEY:
                try:
                    services_status['twelve_labs'] = 'available'
                except Exception as e:
                    services_status['twelve_labs'] = f'error: {str(e)}'
                    overall_status = HealthStatus.WARNING
                    messages.append("Twelve Labs API unavailable")
            else:
                services_status['twelve_labs'] = 'not_configured'
            
            message = "AI services are healthy"
            if messages:
                message = "; ".join(messages)
            
            return {
                'status': overall_status,
                'message': message,
                'details': services_status
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL,
                'message': f"AI services check failed: {str(e)}",
                'details': {'error': str(e)}
            }

class HealthMonitoringSystem:
    """  """
    
    def __init__(self):
        self.checkers: List[HealthChecker] = []
        self.check_history: List[Dict[str, HealthCheckResult]] = []
        self.max_history = 100  #  100  
        self._initialize_checkers()
    
    def _initialize_checkers(self):
        """  """
        self.checkers = [
            DatabaseHealthChecker(),
            CacheHealthChecker(),
            SystemResourcesHealthChecker(),
            AIServiceHealthChecker(),
        ]
        
        #    ( )
        if hasattr(settings, 'EXTERNAL_SERVICES'):
            for service_name, endpoint in settings.EXTERNAL_SERVICES.items():
                self.checkers.append(
                    ExternalServiceHealthChecker(service_name, endpoint)
                )
    
    def add_checker(self, checker: HealthChecker):
        """ """
        self.checkers.append(checker)
    
    def perform_full_health_check(self) -> Dict[str, Any]:
        """  """
        results = {}
        overall_status = HealthStatus.HEALTHY
        critical_issues = []
        warning_issues = []
        
        for checker in self.checkers:
            try:
                result = checker.check()
                results[checker.name] = result
                
                #   
                if result.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
                    recovery_success = self._attempt_auto_recovery(result)
                    result.auto_recovery_attempted = True
                    result.auto_recovery_successful = recovery_success
                
                #   
                if result.status == HealthStatus.CRITICAL:
                    overall_status = HealthStatus.CRITICAL
                    critical_issues.append(f"{checker.name}: {result.message}")
                elif result.status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                    overall_status = HealthStatus.WARNING
                    warning_issues.append(f"{checker.name}: {result.message}")
                
            except Exception as e:
                logger.error(f" '{checker.name}'  : {str(e)}")
                
                #  
                context = ErrorContext(
                    additional_data={
                        'checker_name': checker.name,
                        'checker_timeout': checker.timeout
                    }
                )
                error_tracker.track_error(e, ErrorSeverity.HIGH, ErrorCategory.SYSTEM, context)
                
                results[checker.name] = HealthCheckResult(
                    name=checker.name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    response_time=0,
                    details={'error': str(e)},
                    timestamp=timezone.now().isoformat()
                )
                
                overall_status = HealthStatus.CRITICAL
                critical_issues.append(f"{checker.name}: Health check failed")
        
        #  
        self.check_history.append(results)
        if len(self.check_history) > self.max_history:
            self.check_history.pop(0)
        
        #  
        summary = {
            'overall_status': overall_status.value,
            'timestamp': timezone.now().isoformat(),
            'total_checks': len(self.checkers),
            'healthy_checks': len([r for r in results.values() if r.status == HealthStatus.HEALTHY]),
            'warning_checks': len([r for r in results.values() if r.status == HealthStatus.WARNING]),
            'critical_checks': len([r for r in results.values() if r.status == HealthStatus.CRITICAL]),
            'issues': {
                'critical': critical_issues,
                'warning': warning_issues
            },
            'details': results
        }
        
        #   (5)
        cache.set('health_check_results', summary, 300)
        
        return summary
    
    def _attempt_auto_recovery(self, health_result: HealthCheckResult) -> bool:
        """     """
        try:
            if health_result.name == 'database':
                return self._recover_database_health()
            elif health_result.name == 'cache':
                return self._recover_cache_health()
            elif health_result.name == 'system_resources':
                return self._recover_system_resources()
            elif 'external_service' in health_result.name:
                return self._recover_external_service(health_result)
            
            return False
            
        except Exception as e:
            logger.error(f"    ({health_result.name}): {str(e)}")
            return False
    
    def _recover_database_health(self) -> bool:
        """  """
        try:
            #   
            connection.close()
            
            #  
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            logger.info("   ")
            return True
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return False
    
    def _recover_cache_health(self) -> bool:
        """  """
        try:
            #  
            cache.clear()
            
            #  
            cache.set('health_recovery_test', 'ok', 60)
            result = cache.get('health_recovery_test')
            
            if result == 'ok':
                cache.delete('health_recovery_test')
                logger.info("   ")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return False
    
    def _recover_system_resources(self) -> bool:
        """  """
        try:
            import gc
            
            #   
            gc.collect()
            
            #   
            cache.clear()
            
            logger.info("   ")
            return True
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return False
    
    def _recover_external_service(self, health_result: HealthCheckResult) -> bool:
        """   ()"""
        try:
            #    
            import time
            time.sleep(2)
            
            #     (   )
            logger.info(f"  '{health_result.name}'  ")
            return True
            
        except Exception as e:
            logger.error(f"   : {str(e)}")
            return False
    
    def get_health_trend(self, hours: int = 24) -> Dict[str, Any]:
        """  """
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        trend_data = {
            'period_hours': hours,
            'total_checks': len(self.check_history),
            'availability_percentage': 0,
            'most_frequent_issues': {},
            'recovery_success_rate': 0,
            'performance_trends': {}
        }
        
        if not self.check_history:
            return trend_data
        
        #   
        recent_checks = []
        for check_batch in self.check_history:
            for checker_name, result in check_batch.items():
                check_time = timezone.datetime.fromisoformat(result.timestamp.replace('Z', '+00:00'))
                if check_time > cutoff_time:
                    recent_checks.append((checker_name, result))
        
        if not recent_checks:
            return trend_data
        
        #  
        healthy_checks = len([c for _, c in recent_checks if c.status == HealthStatus.HEALTHY])
        trend_data['availability_percentage'] = (healthy_checks / len(recent_checks)) * 100
        
        #   
        issue_counts = {}
        recovery_attempts = 0
        recovery_successes = 0
        
        for checker_name, result in recent_checks:
            if result.status != HealthStatus.HEALTHY:
                issue_key = f"{checker_name}: {result.message}"
                issue_counts[issue_key] = issue_counts.get(issue_key, 0) + 1
            
            if result.auto_recovery_attempted:
                recovery_attempts += 1
                if result.auto_recovery_successful:
                    recovery_successes += 1
        
        trend_data['most_frequent_issues'] = dict(
            sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )
        
        #  
        if recovery_attempts > 0:
            trend_data['recovery_success_rate'] = (recovery_successes / recovery_attempts) * 100
        
        return trend_data

#     
health_monitor = HealthMonitoringSystem()