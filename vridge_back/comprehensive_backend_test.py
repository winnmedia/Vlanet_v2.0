#!/usr/bin/env python3
"""
VideoPlanet      
  , ,    .
"""

import os
import sys
import json
import time
import requests
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from urllib.parse import urlparse

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_base')
import django
django.setup()

from django.core.management import call_command
from django.db import connection
from django.test.utils import override_settings
from django.core.cache import cache
from django.contrib.auth import get_user_model

#  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('backend_test_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

User = get_user_model()

class BackendSystemValidator:
    """     """
    
    def __init__(self):
        self.base_url = os.environ.get('API_URL', 'http://localhost:8000')
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'server_status': {},
            'database': {},
            'api_endpoints': {},
            'security': {},
            'performance': {},
            'improvements': []
        }
        
    def run_all_tests(self):
        """  """
        logger.info("="*60)
        logger.info("VideoPlanet    ")
        logger.info("="*60)
        
        # 1. Django   
        self.check_django_server()
        
        # 2.     
        self.check_database_connection()
        
        # 3.   
        self.check_migrations()
        
        # 4. API  
        self.test_api_endpoints()
        
        # 5.   
        self.analyze_database_optimization()
        
        # 6.   
        self.check_security_settings()
        
        # 7.  
        self.analyze_performance()
        
        # 8. Redis   
        self.check_redis_cache()
        
        # 9.    
        self.check_error_logging()
        
        # 10.  
        self.generate_improvements()
        
        #  
        self.save_results()
        
    def check_django_server(self):
        """Django   """
        logger.info("\n[1] Django   ")
        
        try:
            #   
            response = requests.get(f"{self.base_url}/api/health/", timeout=5)
            
            if response.status_code == 200:
                self.test_results['server_status'] = {
                    'status': 'running',
                    'response_time': response.elapsed.total_seconds(),
                    'details': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
                logger.info(f"    (: {response.elapsed.total_seconds():.2f})")
            else:
                self.test_results['server_status'] = {
                    'status': 'error',
                    'status_code': response.status_code
                }
                logger.warning(f"   : {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.test_results['server_status'] = {'status': 'not_running'}
            logger.error("    ")
            
    def check_database_connection(self):
        """   """
        logger.info("\n[2]   ")
        
        try:
            with connection.cursor() as cursor:
                # PostgreSQL  
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()[0]
                
                #   
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                table_count = cursor.fetchone()[0]
                
                #   
                cursor.execute("""
                    SELECT pg_database_size(current_database()) / 1024 / 1024 as size_mb;
                """)
                db_size = cursor.fetchone()[0]
                
                self.test_results['database'] = {
                    'status': 'connected',
                    'version': db_version,
                    'table_count': table_count,
                    'size_mb': float(db_size)
                }
                
                logger.info(f"   ")
                logger.info(f"   - : {db_version.split(',')[0]}")
                logger.info(f"   -  : {table_count}")
                logger.info(f"   - : {db_size:.2f} MB")
                
        except Exception as e:
            self.test_results['database']['status'] = 'error'
            self.test_results['database']['error'] = str(e)
            logger.error(f"   : {e}")
            
    def check_migrations(self):
        """  """
        logger.info("\n[3]   ")
        
        try:
            from django.core.management import call_command
            from io import StringIO
            
            out = StringIO()
            call_command('showmigrations', '--list', stdout=out)
            migrations_output = out.getvalue()
            
            #    
            unapplied = []
            for line in migrations_output.split('\n'):
                if '[ ]' in line:
                    unapplied.append(line.strip())
                    
            self.test_results['database']['migrations'] = {
                'status': 'checked',
                'unapplied_count': len(unapplied),
                'unapplied': unapplied[:10]  #  10
            }
            
            if unapplied:
                logger.warning(f"    {len(unapplied)} ")
                for migration in unapplied[:5]:
                    logger.warning(f"   - {migration}")
            else:
                logger.info("    ")
                
        except Exception as e:
            logger.error(f"   : {e}")
            
    def test_api_endpoints(self):
        """API  """
        logger.info("\n[4] API  ")
        
        endpoints = [
            {'path': '/api/auth/login/', 'method': 'POST', 'data': {'email': 'test@test.com', 'password': 'test123'}},
            {'path': '/api/auth/check/', 'method': 'GET'},
            {'path': '/api/projects/', 'method': 'GET'},
            {'path': '/api/feedbacks/', 'method': 'GET'},
            {'path': '/api/video-planning/', 'method': 'GET'},
            {'path': '/api/users/mypage/', 'method': 'GET'},
        ]
        
        for endpoint in endpoints:
            path = endpoint['path']
            method = endpoint['method']
            
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{path}", timeout=5)
                else:
                    response = requests.post(
                        f"{self.base_url}{path}",
                        json=endpoint.get('data', {}),
                        timeout=5
                    )
                    
                self.test_results['api_endpoints'][path] = {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'success': response.status_code in [200, 201, 401, 403]
                }
                
                status_icon = "" if response.status_code in [200, 201] else ""
                logger.info(f"{status_icon} {method} {path}: {response.status_code} ({response.elapsed.total_seconds():.2f})")
                
            except Exception as e:
                self.test_results['api_endpoints'][path] = {
                    'error': str(e),
                    'success': False
                }
                logger.error(f" {method} {path}: {e}")
                
    def analyze_database_optimization(self):
        """  """
        logger.info("\n[5]   ")
        
        optimization_issues = []
        
        try:
            with connection.cursor() as cursor:
                #   
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes
                    WHERE idx_scan = 0
                    AND indexname NOT LIKE '%_pkey'
                    ORDER BY schemaname, tablename;
                """)
                
                unused_indexes = cursor.fetchall()
                if unused_indexes:
                    optimization_issues.append({
                        'type': 'unused_indexes',
                        'count': len(unused_indexes),
                        'details': [f"{idx[1]}.{idx[2]}" for idx in unused_indexes[:5]]
                    })
                    logger.warning(f"    {len(unused_indexes)} ")
                    
                #    (pg_stat_statements  )
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_stat_statements';
                    """)
                    if cursor.fetchone()[0] > 0:
                        cursor.execute("""
                            SELECT 
                                calls,
                                mean_exec_time,
                                query
                            FROM pg_stat_statements
                            WHERE mean_exec_time > 100
                            ORDER BY mean_exec_time DESC
                            LIMIT 5;
                        """)
                        slow_queries = cursor.fetchall()
                        if slow_queries:
                            optimization_issues.append({
                                'type': 'slow_queries',
                                'count': len(slow_queries),
                                'details': [f" {q[1]:.2f}ms" for q in slow_queries]
                            })
                            logger.warning(f"   {len(slow_queries)} ")
                except:
                    pass
                    
                #   vacuum  
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_dead_tup,
                        last_vacuum,
                        last_autovacuum
                    FROM pg_stat_user_tables
                    WHERE n_dead_tup > 1000
                    ORDER BY n_dead_tup DESC
                    LIMIT 5;
                """)
                
                vacuum_needed = cursor.fetchall()
                if vacuum_needed:
                    optimization_issues.append({
                        'type': 'vacuum_needed',
                        'count': len(vacuum_needed),
                        'details': [f"{t[1]} ({t[2]} dead tuples)" for t in vacuum_needed]
                    })
                    logger.warning(f" VACUUM   {len(vacuum_needed)}")
                    
            self.test_results['performance']['db_optimization'] = optimization_issues
            
            if not optimization_issues:
                logger.info("    ")
                
        except Exception as e:
            logger.error(f"    : {e}")
            
    def check_security_settings(self):
        """  """
        logger.info("\n[6]   ")
        
        security_checks = {
            'cors_configured': False,
            'csrf_protection': False,
            'secure_cookies': False,
            'xss_protection': False,
            'rate_limiting': False,
            'jwt_configured': False
        }
        
        try:
            from django.conf import settings
            
            # CORS  
            if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
                security_checks['cors_configured'] = bool(settings.CORS_ALLOWED_ORIGINS)
                logger.info(f" CORS : {len(settings.CORS_ALLOWED_ORIGINS)}  ")
            else:
                logger.warning(" CORS  ")
                
            # CSRF  
            if 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE:
                security_checks['csrf_protection'] = True
                logger.info(" CSRF  ")
            else:
                logger.warning(" CSRF   ")
                
            # Secure Cookies 
            if hasattr(settings, 'SESSION_COOKIE_SECURE'):
                security_checks['secure_cookies'] = settings.SESSION_COOKIE_SECURE
                if settings.SESSION_COOKIE_SECURE:
                    logger.info(" Secure Cookie  ")
                else:
                    logger.warning(" Secure Cookie  ")
                    
            # XSS  
            if hasattr(settings, 'SECURE_BROWSER_XSS_FILTER'):
                security_checks['xss_protection'] = settings.SECURE_BROWSER_XSS_FILTER
                if settings.SECURE_BROWSER_XSS_FILTER:
                    logger.info(" XSS  ")
                    
            # Rate Limiting 
            if 'config.rate_limit_middleware.RateLimitMiddleware' in settings.MIDDLEWARE:
                security_checks['rate_limiting'] = True
                logger.info(" Rate Limiting ")
            else:
                logger.warning(" Rate Limiting  ")
                
            # JWT  
            if hasattr(settings, 'SIMPLE_JWT'):
                security_checks['jwt_configured'] = True
                logger.info(" JWT   ")
                
            self.test_results['security'] = security_checks
            
        except Exception as e:
            logger.error(f"    : {e}")
            
    def analyze_performance(self):
        """ """
        logger.info("\n[7]  ")
        
        performance_metrics = {}
        
        try:
            #   
            endpoints_to_test = [
                '/api/health/',
                '/api/projects/',
                '/api/feedbacks/'
            ]
            
            for endpoint in endpoints_to_test:
                times = []
                for _ in range(3):
                    try:
                        start = time.time()
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                        elapsed = time.time() - start
                        times.append(elapsed)
                    except:
                        pass
                        
                if times:
                    avg_time = sum(times) / len(times)
                    performance_metrics[endpoint] = {
                        'avg_response_time': avg_time,
                        'min_time': min(times),
                        'max_time': max(times)
                    }
                    
                    status = "" if avg_time < 1.0 else ""
                    logger.info(f"{status} {endpoint}:  {avg_time:.3f}")
                    
            #    
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT count(*) FROM pg_stat_activity;
                """)
                active_connections = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT setting FROM pg_settings WHERE name = 'max_connections';
                """)
                max_connections = int(cursor.fetchone()[0])
                
                performance_metrics['db_connections'] = {
                    'active': active_connections,
                    'max': max_connections,
                    'usage_percent': (active_connections / max_connections) * 100
                }
                
                logger.info(f" DB : {active_connections}/{max_connections} ({(active_connections/max_connections)*100:.1f}% )")
                
            self.test_results['performance']['metrics'] = performance_metrics
            
        except Exception as e:
            logger.error(f"   : {e}")
            
    def check_redis_cache(self):
        """Redis   """
        logger.info("\n[8] Redis   ")
        
        if not REDIS_AVAILABLE:
            self.test_results['performance']['redis'] = {'connected': False, 'error': 'redis module not installed'}
            logger.warning(" Redis   ")
            return
            
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
            parsed = urlparse(redis_url)
            
            r = redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                password=parsed.password,
                decode_responses=True
            )
            
            # Redis  
            r.ping()
            
            # Redis  
            info = r.info()
            
            cache_stats = {
                'connected': True,
                'version': info.get('redis_version'),
                'used_memory_mb': info.get('used_memory', 0) / 1024 / 1024,
                'connected_clients': info.get('connected_clients'),
                'total_commands': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
            
            #  
            if cache_stats['keyspace_hits'] + cache_stats['keyspace_misses'] > 0:
                hit_rate = cache_stats['keyspace_hits'] / (cache_stats['keyspace_hits'] + cache_stats['keyspace_misses']) * 100
                cache_stats['hit_rate'] = hit_rate
                logger.info(f" Redis  : {hit_rate:.1f}%")
                
            self.test_results['performance']['redis'] = cache_stats
            logger.info(f" Redis   (v{cache_stats['version']})")
            logger.info(f"   -  : {cache_stats['used_memory_mb']:.2f} MB")
            logger.info(f"   -  : {cache_stats['connected_clients']}")
            
        except:
            self.test_results['performance']['redis'] = {'connected': False}
            logger.warning(" Redis   ")
            
    def check_error_logging(self):
        """   """
        logger.info("\n[9]    ")
        
        logging_checks = {
            'log_files_exist': False,
            'error_tracking': False,
            'log_rotation': False
        }
        
        try:
            #    
            log_dir = os.path.join(os.path.dirname(__file__), 'logs')
            if os.path.exists(log_dir):
                log_files = os.listdir(log_dir)
                logging_checks['log_files_exist'] = len(log_files) > 0
                
                if log_files:
                    logger.info(f"   {len(log_files)} ")
                    for log_file in log_files[:3]:
                        file_path = os.path.join(log_dir, log_file)
                        size_mb = os.path.getsize(file_path) / 1024 / 1024
                        logger.info(f"   - {log_file}: {size_mb:.2f} MB")
                        
            # Django   
            from django.conf import settings
            if hasattr(settings, 'LOGGING'):
                logging_config = settings.LOGGING
                if 'handlers' in logging_config:
                    logging_checks['error_tracking'] = True
                    logger.info(f" Django  : {len(logging_config['handlers'])} ")
                    
            self.test_results['logging'] = logging_checks
            
        except Exception as e:
            logger.error(f"    : {e}")
            
    def generate_improvements(self):
        """ """
        logger.info("\n[10]  ")
        
        improvements = []
        
        #   
        if 'db_optimization' in self.test_results.get('performance', {}):
            for issue in self.test_results['performance']['db_optimization']:
                if issue['type'] == 'unused_indexes':
                    improvements.append({
                        'priority': 'medium',
                        'category': 'database',
                        'issue': f"   {issue['count']}",
                        'solution': '   INSERT/UPDATE  ',
                        'code': 'DROP INDEX IF EXISTS index_name;'
                    })
                elif issue['type'] == 'slow_queries':
                    improvements.append({
                        'priority': 'high',
                        'category': 'performance',
                        'issue': f"  {issue['count']} ",
                        'solution': '    ',
                        'code': 'CREATE INDEX idx_name ON table_name(column_name);'
                    })
                elif issue['type'] == 'vacuum_needed':
                    improvements.append({
                        'priority': 'medium',
                        'category': 'database',
                        'issue': f"VACUUM   {issue['count']}",
                        'solution': 'VACUUM    ',
                        'code': 'VACUUM ANALYZE table_name;'
                    })
                    
        #   
        security = self.test_results.get('security', {})
        if not security.get('rate_limiting'):
            improvements.append({
                'priority': 'high',
                'category': 'security',
                'issue': 'Rate Limiting ',
                'solution': 'DDoS    Rate Limiting ',
                'code': self._get_rate_limiting_code()
            })
            
        if not security.get('secure_cookies'):
            improvements.append({
                'priority': 'high',
                'category': 'security',
                'issue': 'Secure Cookie ',
                'solution': 'HTTPS    ',
                'code': "SESSION_COOKIE_SECURE = True\nCSRF_COOKIE_SECURE = True"
            })
            
        # Redis  
        redis_stats = self.test_results.get('performance', {}).get('redis', {})
        if redis_stats.get('hit_rate', 100) < 80:
            improvements.append({
                'priority': 'medium',
                'category': 'performance',
                'issue': f"   ({redis_stats.get('hit_rate', 0):.1f}%)",
                'solution': '    TTL ',
                'code': self._get_cache_optimization_code()
            })
            
        # API   
        metrics = self.test_results.get('performance', {}).get('metrics', {})
        for endpoint, times in metrics.items():
            if isinstance(times, dict) and times.get('avg_response_time', 0) > 1.0:
                improvements.append({
                    'priority': 'medium',
                    'category': 'performance',
                    'issue': f"{endpoint}   ({times['avg_response_time']:.2f})",
                    'solution': '    ',
                    'code': self._get_query_optimization_code(endpoint)
                })
                
        self.test_results['improvements'] = improvements
        
        #  
        if improvements:
            logger.info(f"\n  {len(improvements)}  :")
            
            #  
            high_priority = [i for i in improvements if i['priority'] == 'high']
            medium_priority = [i for i in improvements if i['priority'] == 'medium']
            
            if high_priority:
                logger.info(f"\n   ({len(high_priority)}):")
                for imp in high_priority:
                    logger.info(f"  - [{imp['category']}] {imp['issue']}")
                    logger.info(f"    → {imp['solution']}")
                    
            if medium_priority:
                logger.info(f"\n   ({len(medium_priority)}):")
                for imp in medium_priority:
                    logger.info(f"  - [{imp['category']}] {imp['issue']}")
                    logger.info(f"    → {imp['solution']}")
        else:
            logger.info("    -   ")
            
    def _get_rate_limiting_code(self):
        """Rate Limiting  """
        return '''# config/rate_limit_middleware.py
from django.core.cache import cache
from django.http import JsonResponse
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # IP  rate limiting
        ip = self.get_client_ip(request)
        cache_key = f"rate_limit_{ip}"
        
        # 1 60 
        requests = cache.get(cache_key, [])
        now = time.time()
        requests = [r for r in requests if r > now - 60]
        
        if len(requests) >= 60:
            return JsonResponse({"error": "Rate limit exceeded"}, status=429)
            
        requests.append(now)
        cache.set(cache_key, requests, 60)
        
        return self.get_response(request)
        
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get(\'HTTP_X_FORWARDED_FOR\')
        if x_forwarded_for:
            ip = x_forwarded_for.split(\',\')[0]
        else:
            ip = request.META.get(\'REMOTE_ADDR\')
        return ip'''
        
    def _get_cache_optimization_code(self):
        """  """
        return '''#   
from django.views.decorators.cache import cache_page
from django.core.cache import cache

#    (5)
@cache_page(60 * 5)
def project_list(request):
    # ...
    
#  
def get_projects(user_id):
    cache_key = f"user_projects_{user_id}"
    projects = cache.get(cache_key)
    
    if projects is None:
        projects = Project.objects.filter(
            user_id=user_id
        ).select_related(\'user\').prefetch_related(\'members\')
        cache.set(cache_key, projects, 300)  # 5 
        
    return projects'''
        
    def _get_query_optimization_code(self, endpoint):
        """  """
        if 'projects' in endpoint:
            return '''# projects/views.py
from django.db.models import Prefetch

def get_queryset(self):
    return Project.objects.select_related(
        \'user\',
        \'basic_plan\'
    ).prefetch_related(
        \'members\',
        \'schedule_set\',
        Prefetch(
            \'files\',
            queryset=File.objects.filter(is_deleted=False)
        )
    ).annotate(
        member_count=Count(\'members\')
    )'''
        elif 'feedbacks' in endpoint:
            return '''# feedbacks/views.py
from django.db.models import Prefetch

def get_queryset(self):
    return Feedback.objects.select_related(
        \'user\',
        \'project\'
    ).prefetch_related(
        Prefetch(
            \'comments\',
            queryset=FeedbackComment.objects.select_related(\'user\')
        )
    ).only(
        \'id\', \'title\', \'video_url\', \'created_at\',
        \'user__name\', \'project__title\'
    )'''
        else:
            return '#      '
            
    def save_results(self):
        """  """
        filename = f"backend_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
        logger.info(f"\n   {filename} ")
        
        #  
        total_issues = len(self.test_results.get('improvements', []))
        high_priority = len([i for i in self.test_results.get('improvements', []) if i['priority'] == 'high'])
        
        logger.info("\n" + "="*60)
        logger.info("  ")
        logger.info("="*60)
        logger.info(f"  : {total_issues}")
        logger.info(f"  : {high_priority}")
        
        if self.test_results.get('server_status', {}).get('status') == 'running':
            logger.info("  : ")
        else:
            logger.info("  : ")
            
        if self.test_results.get('database', {}).get('status') == 'connected':
            logger.info(" : ")
        else:
            logger.info(" : ")
            
        security_score = sum(1 for v in self.test_results.get('security', {}).values() if v)
        logger.info(f"  : {security_score}/6")
        
        
if __name__ == '__main__':
    validator = BackendSystemValidator()
    validator.run_all_tests()