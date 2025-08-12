#!/usr/bin/env python3
"""
Railway 500 에러 진단 도구
"""
import os
import sys
import django

print("=" * 60)
print("Railway 500 에러 진단 시작")
print("=" * 60)

# 1. 환경 변수 확인
print("\n[1] 환경 변수 확인:")
env_vars = [
    'DJANGO_SETTINGS_MODULE',
    'DATABASE_URL',
    'SECRET_KEY',
    'PORT',
    'RAILWAY_ENVIRONMENT'
]
for var in env_vars:
    value = os.environ.get(var, 'NOT SET')
    if var in ['DATABASE_URL', 'SECRET_KEY'] and value != 'NOT SET':
        value = value[:20] + '...'
    print(f"  {var}: {value}")

# 2. Django 설정 로드 테스트
print("\n[2] Django 설정 로드 테스트:")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
try:
    django.setup()
    print("  ✓ Django 설정 로드 성공")
    
    from django.conf import settings
    print(f"  - DEBUG: {settings.DEBUG}")
    print(f"  - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:3]}...")
    print(f"  - INSTALLED_APPS 수: {len(settings.INSTALLED_APPS)}")
    print(f"  - MIDDLEWARE 수: {len(settings.MIDDLEWARE)}")
except Exception as e:
    print(f"  ✗ Django 설정 로드 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 데이터베이스 연결 테스트
print("\n[3] 데이터베이스 연결 테스트:")
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print(f"  ✓ 데이터베이스 연결 성공: {result}")
        
        # 사용자 테이블 확인
        cursor.execute("SELECT COUNT(*) FROM users_user")
        user_count = cursor.fetchone()[0]
        print(f"  - 사용자 수: {user_count}")
except Exception as e:
    print(f"  ✗ 데이터베이스 연결 실패: {e}")

# 4. 미들웨어 스택 검증
print("\n[4] 미들웨어 스택 검증:")
from django.conf import settings
critical_middleware = [
    'corsheaders.middleware.CorsMiddleware',
    'config.middleware.GlobalErrorHandlingMiddleware',
    'config.middleware.RailwayHealthCheckMiddleware'
]
for mw in critical_middleware:
    if mw in settings.MIDDLEWARE:
        print(f"  ✓ {mw.split('.')[-1]}")
    else:
        print(f"  ✗ {mw.split('.')[-1]} 누락!")

# 5. CORS 설정 확인
print("\n[5] CORS 설정 확인:")
cors_settings = [
    'CORS_ALLOWED_ORIGINS',
    'CORS_ALLOW_CREDENTIALS',
    'CORS_ALLOW_HEADERS'
]
for setting in cors_settings:
    value = getattr(settings, setting, None)
    if value:
        if isinstance(value, list):
            print(f"  ✓ {setting}: {len(value)} 항목")
        else:
            print(f"  ✓ {setting}: {value}")
    else:
        print(f"  ✗ {setting}: 설정 안됨")

# 6. URL 라우팅 테스트
print("\n[6] URL 라우팅 테스트:")
from django.urls import reverse, NoReverseMatch
test_urls = [
    ('health', '/health/'),
    ('users:login', '/api/users/login/'),
    ('users:check-auth', '/api/users/check-auth/')
]
for name, expected_path in test_urls:
    try:
        if ':' in name:
            url = reverse(name)
        else:
            # health는 직접 경로 확인
            from django.urls import resolve
            resolve(expected_path)
            url = expected_path
        print(f"  ✓ {name}: {url}")
    except (NoReverseMatch, Exception) as e:
        print(f"  ✗ {name}: {e}")

# 7. 인증 시스템 테스트
print("\n[7] 인증 시스템 테스트:")
try:
    from rest_framework_simplejwt.tokens import RefreshToken
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # 테스트 사용자 확인
    test_user = User.objects.filter(email='demo@test.com').first()
    if test_user:
        print(f"  ✓ 테스트 사용자 존재: {test_user.email}")
        
        # JWT 토큰 생성 테스트
        refresh = RefreshToken.for_user(test_user)
        access = refresh.access_token
        print(f"  ✓ JWT 토큰 생성 성공")
    else:
        print("  ⚠ 테스트 사용자 없음")
except Exception as e:
    print(f"  ✗ 인증 시스템 오류: {e}")

# 8. 권장사항
print("\n[8] 진단 결과 요약:")
print("  Railway 500 에러의 주요 원인:")
print("  1. 미들웨어 스택 순서 문제")
print("  2. CORS 헤더 누락")
print("  3. 데이터베이스 연결 실패")
print("  4. Gunicorn 타임아웃")

print("\n✅ 진단 완료")
print("=" * 60)