"""
    
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.db.migrations.executor import MigrationExecutor
import time
import sys
import os
import platform
import django

# psutil  
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def health_check(request):
    """
      
    , ,   
    """
    health_status = {
        'status': 'healthy',
        'timestamp': int(time.time()),
        'database': 'unknown',
        'cache': 'unknown',
        'filesystem': 'unknown',
        'memory': {},
        'version': {
            'django': django.__version__,
            'python': sys.version.split()[0],
        }
    }
    
    # 1.  
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['database'] = 'ok'
    except Exception as e:
        health_status['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # 2.  
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['cache'] = 'ok'
        else:
            health_status['cache'] = 'error: unable to retrieve'
    except Exception as e:
        health_status['cache'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # 3.  
    try:
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root:
            os.makedirs(media_root, exist_ok=True)
            test_file = os.path.join(media_root, '.health_check')
            with open(test_file, 'w') as f:
                f.write('ok')
            os.remove(test_file)
        health_status['filesystem'] = 'ok'
    except Exception as e:
        health_status['filesystem'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # 4.   (psutil  )
    if HAS_PSUTIL:
        try:
            memory = psutil.virtual_memory()
            health_status['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            }
        except:
            # psutil    
            pass
    
    # HTTP   
    if health_status['status'] == 'unhealthy':
        status_code = 503  # Service Unavailable
    elif health_status['status'] == 'degraded':
        status_code = 200  # OK but degraded
    else:
        status_code = 200  # OK
    
    return JsonResponse(health_status, status=status_code)

@csrf_exempt
@require_http_methods(["GET"])
def api_root(request):
    """
    API  
      API   
    """
    return JsonResponse({
        'message': 'VideoPlanet API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health/',
            'auth': {
                'login': '/api/auth/login/',
                'signup': '/api/auth/signup/',
                'refresh': '/api/auth/refresh/',
                'logout': '/api/auth/logout/',
            },
            'users': {
                'profile': '/api/users/me/',
                'update': '/api/users/update/',
            },
            'projects': {
                'list': '/api/projects/',
                'create': '/api/projects/create/',
                'detail': '/api/projects/{id}/',
            },
            'feedbacks': {
                'list': '/api/feedbacks/',
                'create': '/api/feedbacks/create/',
                'detail': '/api/feedbacks/{id}/',
            },
            'video': {
                'planning': '/api/video-planning/',
                'analysis': '/api/video-analysis/',
            },
            'system': {
                'health': '/api/health/',
                'migrations': '/api/system/migrations/',
                'version': '/api/version/',
            }
        }
    })

def migration_status(request):
    """
       
    """
    try:
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        #  
        applied_migrations = []
        for app_name, migration_name in executor.loader.applied_migrations:
            applied_migrations.append(f"{app_name}.{migration_name}")
        
        #   
        pending_migrations = []
        for migration, backwards in plan:
            if not backwards:
                pending_migrations.append(f"{migration.app_label}.{migration.name}")
        
        return JsonResponse({
            'all_applied': len(pending_migrations) == 0,
            'applied_count': len(applied_migrations),
            'pending_count': len(pending_migrations),
            'applied_migrations': applied_migrations[-10:],  #  10
            'pending_migrations': pending_migrations,
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'all_applied': False
        }, status=500)

def version_info(request):
    """
      
    """
    return JsonResponse({
        'app_name': 'VideoPlanet',
        'app_version': getattr(settings, 'APP_VERSION', '1.0.0'),
        'api_version': '1.0',
        'django_version': django.__version__,
        'python_version': sys.version,
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
        },
        'environment': getattr(settings, 'ENVIRONMENT', 'production'),
        'debug': settings.DEBUG,
    })

@csrf_exempt
@require_http_methods(["OPTIONS", "GET", "POST"])
def options_handler(request):
    """
    OPTIONS   (CORS preflight)
    """
    response = JsonResponse({'status': 'ok'})
    
    # CORS  
    origin = request.headers.get('Origin', '*')
    response['Access-Control-Allow-Origin'] = origin
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Max-Age'] = '86400'  # 24 
    
    return response