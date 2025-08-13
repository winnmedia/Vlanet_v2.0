"""
헬스체크 엔드포인트
Robert - DevOps/Platform Lead
"""

from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.core.cache import cache
import os
from datetime import datetime


class HealthCheckView(View):
    """애플리케이션 헬스체크"""
    
    def get(self, request, *args, **kwargs):
        """헬스체크 상태 반환"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # 1. 데이터베이스 체크
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status['checks']['database'] = 'ok'
        except Exception as e:
            health_status['checks']['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # 2. 캐시 체크 (Redis)
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['checks']['cache'] = 'ok'
            else:
                health_status['checks']['cache'] = 'not configured'
        except Exception:
            health_status['checks']['cache'] = 'not available'
        
        # 3. 디스크 공간 체크
        try:
            import shutil
            disk_usage = shutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            health_status['checks']['disk'] = f'{disk_percent:.1f}% used'
            if disk_percent > 90:
                health_status['status'] = 'unhealthy'
        except Exception:
            health_status['checks']['disk'] = 'unknown'
        
        # 4. 환경변수 체크
        critical_vars = ['SECRET_KEY', 'DATABASE_URL']
        missing_vars = [var for var in critical_vars if not os.environ.get(var)]
        
        if missing_vars:
            health_status['checks']['environment'] = f'missing: {", ".join(missing_vars)}'
            health_status['status'] = 'unhealthy'
        else:
            health_status['checks']['environment'] = 'ok'
        
        # 5. 이메일 설정 체크
        email_configured = all([
            os.environ.get('EMAIL_HOST'),
            os.environ.get('EMAIL_HOST_USER'),
            os.environ.get('EMAIL_HOST_PASSWORD')
        ])
        
        health_status['checks']['email'] = 'configured' if email_configured else 'not configured'
        
        # HTTP 상태 코드 결정
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return JsonResponse(health_status, status=status_code)


class ReadinessCheckView(View):
    """준비 상태 체크 (Kubernetes 스타일)"""
    
    def get(self, request, *args, **kwargs):
        """애플리케이션이 트래픽을 받을 준비가 되었는지 확인"""
        try:
            # 데이터베이스 연결 확인
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # 필수 테이블 존재 확인
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('auth_user', 'django_migrations')
                """)
                count = cursor.fetchone()[0]
                
                if count >= 2:
                    return JsonResponse({'ready': True}, status=200)
                else:
                    return JsonResponse({
                        'ready': False, 
                        'reason': 'Required tables not found'
                    }, status=503)
                    
        except Exception as e:
            return JsonResponse({
                'ready': False,
                'reason': str(e)
            }, status=503)


class LivenessCheckView(View):
    """생존 체크 (애플리케이션이 살아있는지)"""
    
    def get(self, request, *args, **kwargs):
        """애플리케이션 프로세스가 정상인지 확인"""
        return JsonResponse({
            'alive': True,
            'timestamp': datetime.now().isoformat()
        }, status=200)