"""
  API 
 ,  ,  
"""
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import psutil
import redis
import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class MetricsCollector:
    """   """
    
    @staticmethod
    def get_system_metrics():
        """   """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'usage': cpu_percent,
                    'cores': psutil.cpu_count(),
                    'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                },
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'percent': memory.percent,
                    'available': memory.available
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
        except Exception as e:
            logger.error(f"   : {e}")
            return {}
    
    @staticmethod
    def get_database_metrics():
        """  """
        try:
            with connection.cursor() as cursor:
                # PostgreSQL  
                cursor.execute("""
                    SELECT count(*) as connections,
                           sum(case when state = 'active' then 1 else 0 end) as active,
                           sum(case when state = 'idle' then 1 else 0 end) as idle
                    FROM pg_stat_activity
                """)
                conn_stats = cursor.fetchone()
                
                #  
                cursor.execute("""
                    SELECT pg_database_size(current_database()) as size
                """)
                db_size = cursor.fetchone()
                
                #  
                cursor.execute("""
                    SELECT count(*) as slow_queries
                    FROM pg_stat_statements
                    WHERE mean_exec_time > 1000
                """)
                slow_queries = cursor.fetchone() if cursor.description else (0,)
                
                return {
                    'connections': {
                        'total': conn_stats[0] if conn_stats else 0,
                        'active': conn_stats[1] if conn_stats else 0,
                        'idle': conn_stats[2] if conn_stats else 0
                    },
                    'size': db_size[0] if db_size else 0,
                    'slow_queries': slow_queries[0] if slow_queries else 0
                }
        except Exception as e:
            logger.error(f"   : {e}")
            return {}
    
    @staticmethod
    def get_redis_metrics():
        """Redis  """
        try:
            r = redis.from_url(cache._cache.connection_pool.connection_kwargs['url'])
            info = r.info()
            
            return {
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_connections_received': info.get('total_connections_received', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': round(
                    info.get('keyspace_hits', 0) / 
                    max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1), 1) * 100, 
                    2
                )
            }
        except Exception as e:
            logger.error(f"Redis   : {e}")
            return {}
    
    @staticmethod
    def get_application_metrics():
        """  """
        try:
            from django.contrib.sessions.models import Session
            from users.models import User
            from projects.models import Project
            from feedbacks.models import Feedback
            
            now = timezone.now()
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)
            
            #   
            active_sessions = Session.objects.filter(
                expire_date__gte=now
            ).count()
            
            #  
            total_users = User.objects.count()
            active_users_hour = User.objects.filter(
                last_login__gte=hour_ago
            ).count()
            active_users_day = User.objects.filter(
                last_login__gte=day_ago
            ).count()
            new_users_day = User.objects.filter(
                date_joined__gte=day_ago
            ).count()
            
            #  
            total_projects = Project.objects.count()
            active_projects = Project.objects.filter(
                updated_at__gte=day_ago
            ).count()
            
            #  
            total_feedbacks = Feedback.objects.count()
            feedbacks_today = Feedback.objects.filter(
                created_at__gte=day_ago
            ).count()
            
            return {
                'sessions': {
                    'active': active_sessions
                },
                'users': {
                    'total': total_users,
                    'active_hour': active_users_hour,
                    'active_day': active_users_day,
                    'new_today': new_users_day
                },
                'projects': {
                    'total': total_projects,
                    'active': active_projects
                },
                'feedbacks': {
                    'total': total_feedbacks,
                    'today': feedbacks_today
                }
            }
        except Exception as e:
            logger.error(f"   : {e}")
            return {}
    
    @staticmethod
    def get_api_performance_metrics():
        """API   """
        try:
            #  API   
            api_metrics = cache.get('api_performance_metrics', {})
            
            #  
            default_metrics = {
                'login': {'avg_time': 0, 'count': 0, 'errors': 0},
                'projects': {'avg_time': 0, 'count': 0, 'errors': 0},
                'feedback': {'avg_time': 0, 'count': 0, 'errors': 0},
                'planning': {'avg_time': 0, 'count': 0, 'errors': 0},
                'export': {'avg_time': 0, 'count': 0, 'errors': 0}
            }
            
            #  
            for endpoint, data in default_metrics.items():
                if endpoint not in api_metrics:
                    api_metrics[endpoint] = data
            
            return api_metrics
        except Exception as e:
            logger.error(f"API    : {e}")
            return {}

@require_http_methods(["GET"])
def health_check(request):
    """ """
    try:
        #  
        connection.ensure_connection()
        db_status = 'ok'
    except:
        db_status = 'error'
    
    try:
        # Redis 
        cache.get('health_check')
        cache_status = 'ok'
    except:
        cache_status = 'error'
    
    status = 'healthy' if db_status == 'ok' and cache_status == 'ok' else 'unhealthy'
    
    return JsonResponse({
        'status': status,
        'timestamp': timezone.now().isoformat(),
        'database': db_status,
        'cache': cache_status,
        'version': '1.0.15'
    })

@staff_member_required
@require_http_methods(["GET"])
def metrics(request):
    """  """
    collector = MetricsCollector()
    
    metrics_data = {
        'timestamp': timezone.now().isoformat(),
        'system': collector.get_system_metrics(),
        'database': collector.get_database_metrics(),
        'redis': collector.get_redis_metrics(),
        'application': collector.get_application_metrics(),
        'api_performance': collector.get_api_performance_metrics()
    }
    
    # WebSocket  
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'monitoring',
        {
            'type': 'send_metrics',
            'metrics': metrics_data
        }
    )
    
    return JsonResponse(metrics_data)

@staff_member_required
@require_http_methods(["GET"])
@cache_page(60)  # 1 
def system_status(request):
    """  """
    collector = MetricsCollector()
    system_metrics = collector.get_system_metrics()
    
    #  
    warnings = []
    if system_metrics.get('cpu', {}).get('usage', 0) > 80:
        warnings.append('CPU usage high')
    if system_metrics.get('memory', {}).get('percent', 0) > 85:
        warnings.append('Memory usage high')
    if system_metrics.get('disk', {}).get('percent', 0) > 90:
        warnings.append('Disk usage critical')
    
    return JsonResponse({
        'status': 'warning' if warnings else 'ok',
        'warnings': warnings,
        'metrics': system_metrics,
        'timestamp': timezone.now().isoformat()
    })

@staff_member_required
@require_http_methods(["GET"])
def error_logs(request):
    """   """
    #  100   ()
    error_logs = cache.get('recent_error_logs', [])
    
    return JsonResponse({
        'logs': error_logs[-100:],  #  100
        'total': len(error_logs),
        'timestamp': timezone.now().isoformat()
    })

@staff_member_required
@require_http_methods(["POST"])
def trigger_alert(request):
    """  """
    try:
        data = json.loads(request.body)
        message = data.get('message', 'Manual alert triggered')
        severity = data.get('severity', 'info')
        
        # WebSocket  
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'monitoring',
            {
                'type': 'send_alert',
                'alert': {
                    'message': message,
                    'severity': severity,
                    'timestamp': timezone.now().isoformat()
                }
            }
        )
        
        # Slack  ( )
        if severity in ['error', 'critical']:
            send_slack_alert(message, severity)
        
        return JsonResponse({'status': 'success', 'message': 'Alert sent'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def send_slack_alert(message, severity='info'):
    """Slack  """
    import requests
    from django.conf import settings
    
    webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
    if not webhook_url:
        return
    
    color_map = {
        'info': '#36a64f',
        'warning': '#ff9900',
        'error': '#ff0000',
        'critical': '#990000'
    }
    
    payload = {
        'text': f'VideoPlanet  ',
        'attachments': [{
            'color': color_map.get(severity, '#36a64f'),
            'fields': [
                {
                    'title': 'Severity',
                    'value': severity.upper(),
                    'short': True
                },
                {
                    'title': 'Time',
                    'value': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'short': True
                },
                {
                    'title': 'Message',
                    'value': message,
                    'short': False
                }
            ]
        }]
    }
    
    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        logger.error(f"Slack   : {e}")