#!/usr/bin/env python3
"""
Railway 최종 배포 검증 스크립트
Victoria - DBRE (Database Reliability Engineer)

배포 전 모든 시스템이 정상 동작하는지 확인
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

def print_banner(title):
    """배너 출력"""
    print("=" * 80)
    print(f" {title}")
    print("=" * 80)

def check_environment_variables():
    """필수 환경 변수 확인"""
    print_banner("환경 변수 확인")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'DJANGO_SETTINGS_MODULE'
    ]
    
    optional_vars = [
        'DEBUG',
        'REDIS_URL',
        'EMAIL_HOST_USER',
        'PORT'
    ]
    
    all_vars_ok = True
    
    print("필수 환경 변수:")
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            masked_value = f"{value[:10]}..." if len(value) > 10 else value
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: MISSING")
            all_vars_ok = False
    
    print("\n선택적 환경 변수:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            masked_value = f"{value[:10]}..." if len(value) > 10 else value
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ⚠️ {var}: Not Set")
    
    return all_vars_ok

def check_django_setup():
    """Django 설정 확인"""
    print_banner("Django 설정 확인")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
        import django
        django.setup()
        
        from django.conf import settings
        print("✅ Django 설정 로드 성공")
        print(f"  - DEBUG: {settings.DEBUG}")
        print(f"  - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:3]}")
        print(f"  - 설치된 앱 수: {len(settings.INSTALLED_APPS)}")
        print(f"  - 데이터베이스 엔진: {settings.DATABASES['default']['ENGINE']}")
        
        return True
    except Exception as e:
        print(f"❌ Django 설정 실패: {e}")
        return False

def check_database_connection():
    """데이터베이스 연결 확인"""
    print_banner("데이터베이스 연결 확인")
    
    try:
        from django.db import connection
        
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT version(), current_database(), current_user")
            result = cursor.fetchone()
        
        connection_time = (time.time() - start_time) * 1000
        
        print(f"✅ PostgreSQL 연결 성공 ({connection_time:.2f}ms)")
        print(f"  - Version: {result[0][:50]}...")
        print(f"  - Database: {result[1]}")
        print(f"  - User: {result[2]}")
        
        # 연결 풀 상태 확인
        cursor.execute("""
            SELECT count(*) as total_connections,
                   count(*) filter (where state = 'active') as active,
                   count(*) filter (where state = 'idle') as idle
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)
        pool_info = cursor.fetchone()
        print(f"  - 연결 풀: Total={pool_info[0]}, Active={pool_info[1]}, Idle={pool_info[2]}")
        
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False

def check_user_model():
    """사용자 모델 확인"""
    print_banner("사용자 모델 확인")
    
    try:
        from users.models import User
        
        # 사용자 통계
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        print(f"✅ 사용자 모델 접근 성공")
        print(f"  - 전체 사용자: {total_users}")
        print(f"  - 활성 사용자: {active_users}")
        print(f"  - 관리자: {staff_users}")
        
        # Demo 사용자 확인
        try:
            demo_user = User.objects.get(email='demo@test.com')
            print(f"  - Demo 사용자: ✅ 존재 (ID: {demo_user.id})")
        except User.DoesNotExist:
            print(f"  - Demo 사용자: ❌ 없음")
        
        return True
    except Exception as e:
        print(f"❌ 사용자 모델 확인 실패: {e}")
        return False

def test_authentication():
    """인증 시스템 테스트"""
    print_banner("인증 시스템 테스트")
    
    try:
        from django.contrib.auth import authenticate
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Demo 사용자 인증
        user = authenticate(username='demo@test.com', password='123456')
        
        if user:
            print("✅ Demo 사용자 인증 성공")
            print(f"  - User ID: {user.id}")
            print(f"  - Email: {user.email}")
            
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            print("✅ JWT 토큰 생성 성공")
            print(f"  - Access Token: {access_token[:30]}...")
            
            return True
        else:
            print("❌ Demo 사용자 인증 실패")
            return False
            
    except Exception as e:
        print(f"❌ 인증 시스템 테스트 실패: {e}")
        return False

def check_migrations():
    """마이그레이션 상태 확인"""
    print_banner("마이그레이션 상태 확인")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # 최신 마이그레이션 확인
            cursor.execute("""
                SELECT app, name, applied
                FROM django_migrations 
                WHERE app IN ('users', 'auth', 'contenttypes', 'sessions')
                ORDER BY applied DESC
                LIMIT 10
            """)
            
            recent_migrations = cursor.fetchall()
            print(f"✅ 최근 마이그레이션 {len(recent_migrations)}개 확인:")
            
            for app, name, applied in recent_migrations:
                print(f"  - {app}: {name} ({applied})")
            
            # users 앱 특별 확인
            cursor.execute("""
                SELECT COUNT(*) FROM django_migrations 
                WHERE app = 'users'
            """)
            users_migrations = cursor.fetchone()[0]
            print(f"  - Users 앱 마이그레이션: {users_migrations}개")
            
        return True
    except Exception as e:
        print(f"❌ 마이그레이션 확인 실패: {e}")
        return False

def performance_benchmark():
    """성능 벤치마크"""
    print_banner("성능 벤치마크")
    
    try:
        from django.db import connection
        from users.models import User
        
        # 1. 단순 쿼리 성능
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        simple_query_time = (time.time() - start_time) * 1000
        
        # 2. 복잡한 쿼리 성능
        start_time = time.time()
        User.objects.filter(is_active=True).count()
        complex_query_time = (time.time() - start_time) * 1000
        
        # 3. 인증 성능
        start_time = time.time()
        from django.contrib.auth import authenticate
        authenticate(username='demo@test.com', password='123456')
        auth_time = (time.time() - start_time) * 1000
        
        print("✅ 성능 벤치마크:")
        print(f"  - 단순 쿼리: {simple_query_time:.2f}ms")
        print(f"  - 복잡한 쿼리: {complex_query_time:.2f}ms")
        print(f"  - 인증 처리: {auth_time:.2f}ms")
        
        # 성능 경고
        if simple_query_time > 100:
            print("  ⚠️ 단순 쿼리가 느림 (>100ms)")
        if complex_query_time > 500:
            print("  ⚠️ 복잡한 쿼리가 느림 (>500ms)")
        if auth_time > 1000:
            print("  ⚠️ 인증이 느림 (>1000ms)")
        
        return True
    except Exception as e:
        print(f"❌ 성능 벤치마크 실패: {e}")
        return False

def test_railway_endpoints():
    """Railway 전용 엔드포인트 테스트"""
    print_banner("Railway 엔드포인트 테스트 (로컬)")
    
    # 로컬 서버가 실행 중인지 확인
    test_urls = [
        'http://127.0.0.1:8001/api/users/railway/health/',
        'http://127.0.0.1:8001/api/users/railway/status/',
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - 정상")
                data = response.json()
                if 'status' in data:
                    print(f"  - Status: {data['status']}")
            else:
                print(f"⚠️ {url} - HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ {url} - 연결 실패 (서버 미실행)")
        except Exception as e:
            print(f"❌ {url} - 오류: {e}")

def generate_deployment_summary():
    """배포 요약 생성"""
    print_banner("배포 요약")
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'environment': 'railway',
        'checks_passed': [],
        'checks_failed': [],
        'warnings': []
    }
    
    # 각 체크 결과 요약
    checks = [
        ('환경 변수', check_environment_variables()),
        ('Django 설정', check_django_setup()),
        ('데이터베이스 연결', check_database_connection()),
        ('사용자 모델', check_user_model()),
        ('인증 시스템', test_authentication()),
        ('마이그레이션', check_migrations()),
        ('성능 벤치마크', performance_benchmark())
    ]
    
    for check_name, result in checks:
        if result:
            summary['checks_passed'].append(check_name)
        else:
            summary['checks_failed'].append(check_name)
    
    # 결과 출력
    total_checks = len(checks)
    passed_checks = len(summary['checks_passed'])
    success_rate = (passed_checks / total_checks) * 100
    
    print(f"전체 검사 결과: {passed_checks}/{total_checks} 통과 ({success_rate:.1f}%)")
    
    if summary['checks_failed']:
        print("\n❌ 실패한 검사:")
        for check in summary['checks_failed']:
            print(f"  - {check}")
    
    if success_rate >= 85:
        print("\n✅ 배포 준비 완료!")
        deployment_ready = True
    else:
        print("\n⚠️ 일부 문제가 있습니다. 검토 후 배포하세요.")
        deployment_ready = False
    
    # 배포 명령어 출력
    if deployment_ready:
        print("\n" + "=" * 50)
        print("Railway 배포 명령어:")
        print("./railway_start_unified.sh")
        print("=" * 50)
    
    return summary

def main():
    """메인 실행 함수"""
    print_banner(f"Railway 최종 배포 검증 - {datetime.now()}")
    
    try:
        summary = generate_deployment_summary()
        
        # 요약을 JSON 파일로 저장
        with open('railway_deploy_check_result.json', 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n검증 결과가 railway_deploy_check_result.json에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ 배포 검증 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()