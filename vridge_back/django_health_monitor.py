#!/usr/bin/env python3
"""
Django 헬스 모니터링 및 진단 도구
Django 서버의 상태를 확인하고 문제를 진단합니다.
"""
import os
import sys
import django
import json
from datetime import datetime

# Django 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

def check_database():
    """데이터베이스 연결 확인"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_migrations():
    """마이그레이션 상태 확인"""
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
    """설치된 앱 확인"""
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
    """정적 파일 설정 확인"""
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
    """미들웨어 설정 확인"""
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
    """전체 헬스 체크 실행"""
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
    
    # 전체 상태 판단
    all_healthy = all(
        check.get("status") in ["healthy", "pending"] 
        for check in report["checks"].values()
    )
    
    report["overall_status"] = "healthy" if all_healthy else "unhealthy"
    
    # 결과 출력
    print(json.dumps(report, indent=2))
    
    # 종료 코드
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()