"""
    
"""

import time
import logging
import functools
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils.decorators import method_decorator


logger = logging.getLogger('performance')


class PerformanceMonitor:
    """
      
    """
    
    def __init__(self):
        self.metrics = {
            'db_queries': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'slow_requests': [],
            'api_calls': {},
        }
    
    def log_db_query(self, query, duration):
        """  """
        if duration > 0.1:  # 100ms 
            self.metrics['db_queries'].append({
                'query': query,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
    
    def log_cache_hit(self):
        """  """
        self.metrics['cache_hits'] += 1
    
    def log_cache_miss(self):
        """  """
        self.metrics['cache_misses'] += 1
    
    def log_slow_request(self, path, duration):
        """  """
        if duration > 1.0:  # 1 
            self.metrics['slow_requests'].append({
                'path': path,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_metrics(self):
        """ """
        return self.metrics.copy()
    
    def reset_metrics(self):
        """ """
        self.metrics = {
            'db_queries': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'slow_requests': [],
            'api_calls': {},
        }


#   
monitor = PerformanceMonitor()


# 

def measure_time(func):
    """   """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"{func.__name__}  : {duration:.3f}")
        
        return result
    return wrapper


def cache_result(timeout=300, key_prefix=''):
    """  """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            #   
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            #  
            cached = cache.get(cache_key)
            if cached is not None:
                monitor.log_cache_hit()
                return cached
            
            #  
            monitor.log_cache_miss()
            result = func(*args, **kwargs)
            
            #  
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def optimize_db_queries(func):
    """   """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        #   
        initial_queries = len(connection.queries)
        
        result = func(*args, **kwargs)
        
        #   
        query_count = len(connection.queries) - initial_queries
        
        if query_count > 10:
            logger.warning(f"{func.__name__} {query_count}   ( )")
        
        return result
    return wrapper


# 

class PerformanceMiddleware:
    """
       
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        #   
        start_time = time.time()
        
        #   
        initial_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        #   
        duration = time.time() - start_time
        
        #   
        query_count = len(connection.queries) - initial_queries
        
        #   
        if duration > 1.0:
            monitor.log_slow_request(request.path, duration)
            logger.warning(f" : {request.path} ({duration:.2f}, {query_count} )")
        
        #      ( )
        if settings.DEBUG:
            response['X-Response-Time'] = f"{duration:.3f}"
            response['X-DB-Query-Count'] = str(query_count)
        
        return response


#   

def analyze_queries():
    """
      
    """
    from django.db import connection
    from collections import defaultdict
    
    query_stats = defaultdict(lambda: {'count': 0, 'total_time': 0})
    
    for query in connection.queries:
        sql = query['sql']
        time = float(query.get('time', 0))
        
        #  
        table_name = 'unknown'
        if 'FROM' in sql:
            parts = sql.split('FROM')[1].split()
            if parts:
                table_name = parts[0].strip('"').strip('`')
        
        query_stats[table_name]['count'] += 1
        query_stats[table_name]['total_time'] += time
    
    #  
    print("\n   :")
    print("-" * 80)
    print(f"{'':<30} {' ':<10} {' ()':<15} {' ()':<15}")
    print("-" * 80)
    
    for table, stats in sorted(query_stats.items(), 
                               key=lambda x: x[1]['total_time'], 
                               reverse=True):
        avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
        print(f"{table:<30} {stats['count']:<10} "
              f"{stats['total_time']:<15.3f} {avg_time:<15.3f}")
    
    total_queries = sum(s['count'] for s in query_stats.values())
    total_time = sum(s['total_time'] for s in query_stats.values())
    
    print("-" * 80)
    print(f"{'':<30} {total_queries:<10} {total_time:<15.3f}")
    print("\n  :")
    
    #  
    for table, stats in query_stats.items():
        if stats['count'] > 10:
            print(f"  - {table}: select_related()  prefetch_related()  ")
        if stats['total_time'] > 0.5:
            print(f"  - {table}:   ")


#  

def warm_cache():
    """
        
    """
    from projects.models import Project
    from users.models import User
    
    print("   ...")
    
    #   
    active_projects = Project.objects.filter(
        is_active=True
    ).select_related('user', 'feedback').prefetch_related('member_list')
    
    for project in active_projects:
        cache_key = f"project:{project.id}"
        cache.set(cache_key, project, 3600)
    
    print(f" {active_projects.count()}   ")
    
    #   
    active_users = User.objects.filter(
        is_active=True,
        last_login__isnull=False
    )
    
    for user in active_users:
        cache_key = f"user:{user.id}"
        cache.set(cache_key, user, 3600)
    
    print(f" {active_users.count()}   ")


#  

def load_test(url, num_requests=100, num_concurrent=10):
    """
      
    """
    import concurrent.futures
    import requests
    
    print(f"   : {url}")
    print(f"    : {num_requests}")
    print(f"    : {num_concurrent}")
    
    def make_request():
        start = time.time()
        try:
            response = requests.get(url, timeout=30)
            duration = time.time() - start
            return {
                'status': response.status_code,
                'duration': duration,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'status': 0,
                'duration': time.time() - start,
                'success': False,
                'error': str(e)
            }
    
    #  
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    #  
    successful = sum(1 for r in results if r['success'])
    failed = num_requests - successful
    durations = [r['duration'] for r in results if r['success']]
    
    if durations:
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
    else:
        avg_duration = min_duration = max_duration = 0
    
    print("\n  :")
    print(f"   : {successful}/{num_requests} ({successful/num_requests*100:.1f}%)")
    print(f"   : {failed}")
    print(f"     : {avg_duration:.3f}")
    print(f"     : {min_duration:.3f}")
    print(f"     : {max_duration:.3f}")
    print(f"   : {successful/sum(durations):.1f} req/sec" if durations else "")


#   

def suggest_indexes():
    """
      
    """
    suggestions = []
    
    #    
    common_lookups = {
        'projects.Project': ['user', 'created', 'is_active'],
        'feedbacks.FeedBack': ['project', 'created'],
        'feedbacks.FeedBackItem': ['feedback', 'user', 'created'],
        'users.User': ['email', 'username', 'is_active'],
    }
    
    for model_path, fields in common_lookups.items():
        app_label, model_name = model_path.split('.')
        
        for field in fields:
            suggestions.append({
                'model': model_name,
                'field': field,
                'sql': f"CREATE INDEX idx_{model_name.lower()}_{field} "
                      f"ON {app_label}_{model_name.lower()} ({field});"
            })
    
    print("\n   :")
    for suggestion in suggestions:
        print(f"\n: {suggestion['model']}")
        print(f": {suggestion['field']}")
        print(f"SQL: {suggestion['sql']}")
    
    return suggestions


# Sentry  ( )

def setup_sentry():
    """
    Sentry 
    """
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
                RedisIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% 
            send_default_pii=False,  #   
            environment=settings.ENVIRONMENT,
            release=settings.VERSION,
            
            #  
            profiles_sample_rate=0.1,
            
            # 
            before_send=lambda event, hint: event if not settings.DEBUG else None,
            
            #  
            ignore_errors=[
                'KeyboardInterrupt',
                'SystemExit',
                'Http404',
            ],
        )
        
        logger.info("Sentry  ")