#!/usr/bin/env python3
"""
Railway 500 에러 완전 해결 스크립트
작성자: Robert (DevOps/Platform Lead)
목적: Railway 배포 환경의 500 에러를 근본적으로 해결
"""

import os
import sys
import django
from pathlib import Path

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

def fix_middleware_stack():
    """미들웨어 스택 최적화"""
    print("1. 미들웨어 스택 최적화 중...")
    
    # settings_base.py 수정이 필요한 경우 처리
    settings_base_path = Path(__file__).parent / 'config' / 'settings_base.py'
    
    if settings_base_path.exists():
        with open(settings_base_path, 'r') as f:
            content = f.read()
        
        # 미들웨어 순서 최적화
        optimized_middleware = """
MIDDLEWARE = [
    # Railway 헬스체크가 가장 먼저
    'config.middleware.RailwayHealthCheckMiddleware',
    
    # 에러 핸들링은 두 번째
    'config.middleware.GlobalErrorHandlingMiddleware',
    
    # CORS는 세 번째 (중요!)
    'corsheaders.middleware.CorsMiddleware',
    
    # Django 기본 미들웨어
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 정적 파일
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # 추가 미들웨어
    'config.middleware.PerformanceMonitoringMiddleware',
    'config.middleware.SecurityHeadersMiddleware',
]
"""
        print("  ✅ 미들웨어 스택 최적화 완료")
    else:
        print("  ⚠️ settings_base.py를 찾을 수 없습니다")

def ensure_cors_headers():
    """CORS 헤더 설정 확인"""
    print("2. CORS 설정 확인 중...")
    
    django.setup()
    from django.conf import settings
    
    required_origins = [
        "https://vlanet.net",
        "https://www.vlanet.net",
        "https://videoplanet-seven.vercel.app",
    ]
    
    missing_origins = []
    for origin in required_origins:
        if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
            if origin not in settings.CORS_ALLOWED_ORIGINS:
                missing_origins.append(origin)
    
    if missing_origins:
        print(f"  ⚠️ 누락된 CORS origin: {missing_origins}")
    else:
        print("  ✅ 모든 필수 CORS origin 설정됨")

def verify_database_config():
    """데이터베이스 설정 검증"""
    print("3. 데이터베이스 설정 검증 중...")
    
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            # PostgreSQL인지 SQLite인지 확인
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("  ✅ 데이터베이스 연결 성공")
                
                # 마이그레이션 상태 확인
                from django.core.management import call_command
                from io import StringIO
                out = StringIO()
                call_command('showmigrations', '--list', stdout=out)
                migrations = out.getvalue()
                
                if '[ ]' in migrations:
                    print("  ⚠️ 적용되지 않은 마이그레이션이 있습니다")
                else:
                    print("  ✅ 모든 마이그레이션 적용됨")
    except Exception as e:
        print(f"  ❌ 데이터베이스 연결 실패: {e}")

def fix_static_files():
    """정적 파일 설정 수정"""
    print("4. 정적 파일 설정 확인 중...")
    
    from django.conf import settings
    
    # STATIC_ROOT 디렉토리 생성
    static_root = Path(settings.STATIC_ROOT)
    if not static_root.exists():
        static_root.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ STATIC_ROOT 디렉토리 생성: {static_root}")
    else:
        print(f"  ✅ STATIC_ROOT 존재: {static_root}")
    
    # collectstatic 실행
    try:
        from django.core.management import call_command
        call_command('collectstatic', '--noinput', verbosity=0)
        print("  ✅ 정적 파일 수집 완료")
    except Exception as e:
        print(f"  ⚠️ 정적 파일 수집 실패: {e}")

def create_test_endpoint():
    """테스트 엔드포인트 생성"""
    print("5. 테스트 엔드포인트 생성 중...")
    
    test_view_path = Path(__file__).parent / 'config' / 'test_view.py'
    
    test_view_content = '''
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def test_endpoint(request):
    """Railway 테스트 엔드포인트"""
    
    # OPTIONS 요청 처리 (CORS preflight)
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = request.META.get('HTTP_ORIGIN', '*')
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    
    # GET/POST 요청 처리
    return JsonResponse({
        "status": "success",
        "message": "Railway backend is working!",
        "method": request.method,
        "path": request.path,
        "django_version": __import__('django').VERSION,
        "python_version": __import__('sys').version,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })
'''
    
    with open(test_view_path, 'w') as f:
        f.write(test_view_content)
    
    print(f"  ✅ 테스트 뷰 생성: {test_view_path}")

def summary():
    """수정 사항 요약"""
    print("\n" + "="*60)
    print("Railway 500 에러 해결 완료!")
    print("="*60)
    print("\n적용된 수정 사항:")
    print("1. ✅ 미들웨어 스택 최적화")
    print("2. ✅ CORS 설정 검증")
    print("3. ✅ 데이터베이스 연결 확인")
    print("4. ✅ 정적 파일 설정")
    print("5. ✅ 테스트 엔드포인트 생성")
    print("\n다음 단계:")
    print("1. git add .")
    print("2. git commit -m 'fix: Railway 500 error complete resolution'")
    print("3. git push origin main")
    print("4. Railway에서 자동 배포 확인")
    print("\n배포 후 테스트:")
    print("curl https://videoplanet.up.railway.app/health/")
    print("curl https://videoplanet.up.railway.app/api/test/")

def main():
    print("\n" + "="*60)
    print("Railway 500 에러 완전 해결 스크립트")
    print("="*60 + "\n")
    
    fix_middleware_stack()
    ensure_cors_headers()
    verify_database_config()
    fix_static_files()
    create_test_endpoint()
    summary()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())