#!/usr/bin/env python3
"""
Django     
Django     .
"""
import os
import sys
import django
import json
from datetime import datetime

# Django  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

def check_database():
    """  """
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_migrations():
    """  """
    try:
        from django.core.management import call_command
        from io import StringIO
        output = StringIO()
        call_command('showmigrations', '--plan', stdout=output)
        migrations = output.getvalue()
        
        unapplied = migrations.count('[ ]')
        applied = migrations.count('[X]')
        
        return {
            "status": "healthy" if unapplied == 0 else "pending",
            "applied": applied,
            "unapplied": unapplied
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_apps():
    """  """
    try:
        django.setup()
        from django.apps import apps
        app_list = [app.label for app in apps.get_app_configs()]
        return {
            "status": "healthy",
            "apps": app_list,
            "count": len(app_list)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_static_files():
    """   """
    try:
        from django.conf import settings
        return {
            "status": "healthy",
            "STATIC_URL": settings.STATIC_URL,
            "STATIC_ROOT": str(settings.STATIC_ROOT),
            "STATICFILES_DIRS": [str(d) for d in getattr(settings, 'STATICFILES_DIRS', [])]
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_middleware():
    """  """
    try:
        from django.conf import settings
        middleware = settings.MIDDLEWARE
        return {
            "status": "healthy",
            "middleware": middleware,
            "count": len(middleware)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    """   """
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": os.environ.get('DJANGO_SETTINGS_MODULE'),
        "checks": {
            "database": check_database(),
            "migrations": check_migrations(),
            "apps": check_apps(),
            "static_files": check_static_files(),
            "middleware": check_middleware()
        }
    }
    
    #   
    all_healthy = all(
        check.get("status") in ["healthy", "pending"] 
        for check in report["checks"].values()
    )
    
    report["overall_status"] = "healthy" if all_healthy else "unhealthy"
    
    #  
    print(json.dumps(report, indent=2))
    
    #  
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()