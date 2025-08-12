"""
Health Check and Monitoring Module for Railway Deployment
Provides comprehensive health checking and system monitoring
"""
import os
import sys
import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)

class HealthCheckService:
    """Service for comprehensive health checks"""
    
    @staticmethod
    def check_database():
        """Check database connectivity and performance"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return {
                    "status": "healthy",
                    "response_time": connection.queries[-1]['time'] if connection.queries else "0ms",
                    "database": settings.DATABASES['default']['ENGINE'].split('.')[-1]
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database": "unknown"
            }
    
    @staticmethod
    def check_cache():
        """Check cache connectivity"""
        try:
            test_key = f"health_check_{datetime.now().timestamp()}"
            cache.set(test_key, "test", 10)
            value = cache.get(test_key)
            cache.delete(test_key)
            
            if value == "test":
                return {
                    "status": "healthy",
                    "backend": settings.CACHES['default']['BACKEND'].split('.')[-1]
                }
            else:
                return {
                    "status": "degraded",
                    "message": "Cache write/read mismatch"
                }
        except Exception as e:
            logger.warning(f"Cache health check failed: {e}")
            return {
                "status": "degraded",
                "error": str(e),
                "message": "Cache unavailable but system operational"
            }
    
    @staticmethod
    def check_disk_space():
        """Check available disk space"""
        if not PSUTIL_AVAILABLE:
            return {
                "status": "unknown",
                "message": "psutil not available for disk metrics"
            }
        
        try:
            disk_usage = psutil.disk_usage('/')
            return {
                "status": "healthy" if disk_usage.percent < 90 else "warning",
                "used_percent": disk_usage.percent,
                "free_gb": round(disk_usage.free / (1024**3), 2)
            }
        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    @staticmethod
    def check_memory():
        """Check memory usage"""
        if not PSUTIL_AVAILABLE:
            return {
                "status": "unknown",
                "message": "psutil not available for memory metrics"
            }
        
        try:
            memory = psutil.virtual_memory()
            return {
                "status": "healthy" if memory.percent < 90 else "warning",
                "used_percent": memory.percent,
                "available_mb": round(memory.available / (1024**2), 2)
            }
        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    @staticmethod
    def check_critical_settings():
        """Verify critical Django settings"""
        issues = []
        
        # Check SECRET_KEY
        if settings.SECRET_KEY == 'django-insecure-production-key-change-me':
            issues.append("SECRET_KEY not properly configured")
        
        # Check ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS and not settings.DEBUG:
            issues.append("ALLOWED_HOSTS contains wildcard in production")
        
        # Check DEBUG mode
        if settings.DEBUG and os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
            issues.append("DEBUG mode enabled in production")
        
        return {
            "status": "healthy" if not issues else "warning",
            "issues": issues,
            "debug": settings.DEBUG,
            "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')
        }
    
    @staticmethod
    def check_static_files():
        """Check static files configuration"""
        static_info = {
            "STATIC_URL": settings.STATIC_URL,
            "STATIC_ROOT": str(settings.STATIC_ROOT),
            "STATICFILES_DIRS": [str(d) for d in settings.STATICFILES_DIRS],
            "static_root_exists": os.path.exists(settings.STATIC_ROOT),
            "staticfiles_dirs_exist": [os.path.exists(d) for d in settings.STATICFILES_DIRS]
        }
        
        # Check if any static directory exists
        has_static = static_info["static_root_exists"] or any(static_info["staticfiles_dirs_exist"])
        
        return {
            "status": "healthy" if has_static else "warning",
            "message": "Static files configured" if has_static else "No static files found",
            "details": static_info
        }
    
    @classmethod
    def full_check(cls):
        """Perform complete health check"""
        checks = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "environment": {
                "railway": os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
                "python": sys.version.split()[0],
                "django": os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown')
            },
            "checks": {
                "database": cls.check_database(),
                "cache": cls.check_cache(),
                "disk": cls.check_disk_space(),
                "memory": cls.check_memory(),
                "settings": cls.check_critical_settings(),
                "static_files": cls.check_static_files()
            }
        }
        
        # Determine overall status
        for check in checks["checks"].values():
            if check.get("status") == "unhealthy":
                checks["status"] = "unhealthy"
                break
            elif check.get("status") == "warning" and checks["status"] != "unhealthy":
                checks["status"] = "degraded"
        
        return checks


def health_check_view(request):
    """
    Health check endpoint for Railway and monitoring services
    Returns different levels of detail based on query parameters
    """
    # Basic health check (for Railway health check)
    if request.GET.get('basic') == 'true':
        try:
            # Quick database ping
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return JsonResponse({"status": "ok"}, status=200)
        except Exception as e:
            logger.error(f"Basic health check failed: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=503)
    
    # Full health check
    try:
        health_data = HealthCheckService.full_check()
        status_code = 200 if health_data["status"] == "healthy" else 503 if health_data["status"] == "unhealthy" else 200
        return JsonResponse(health_data, status=status_code)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status=503)


def readiness_check_view(request):
    """
    Readiness check for Railway deployment
    Checks if the application is ready to receive traffic
    """
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check critical settings
        if settings.SECRET_KEY == 'django-insecure-production-key-change-me':
            return JsonResponse({
                "ready": False,
                "reason": "Configuration not complete"
            }, status=503)
        
        return JsonResponse({
            "ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }, status=200)
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            "ready": False,
            "error": str(e)
        }, status=503)


def liveness_check_view(request):
    """
    Liveness check for Railway deployment
    Simple check to verify the application is running
    """
    return JsonResponse({
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "pid": os.getpid()
    }, status=200)