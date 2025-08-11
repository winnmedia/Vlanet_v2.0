#!/usr/bin/env python
"""
백엔드 API 오류 수정 스크립트
- 데이터베이스 마이그레이션 문제 해결
- URL 라우팅 검증
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

from django.db import connection
from django.core.management import call_command

def fix_deletion_reason_field():
    """deletion_reason 필드 NULL 제약 조건 수정"""
    print("🔧 Fixing deletion_reason field constraint...")
    
    with connection.cursor() as cursor:
        # 현재 스키마 확인
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='users_user';
        """)
        result = cursor.fetchone()
        if result:
            print(f"Current schema: {result[0][:200]}...")
        
        # deletion_reason 필드를 NULL 허용으로 변경
        try:
            cursor.execute("""
                ALTER TABLE users_user 
                ALTER COLUMN deletion_reason DROP NOT NULL;
            """)
            print("✅ Successfully modified deletion_reason constraint")
        except Exception as e:
            # SQLite는 ALTER COLUMN을 지원하지 않으므로 다른 방법 사용
            print(f"⚠️  SQLite detected, using alternative method: {e}")
            
            # 기본값 설정으로 해결
            cursor.execute("""
                UPDATE users_user 
                SET deletion_reason = '' 
                WHERE deletion_reason IS NULL;
            """)
            print("✅ Set default values for NULL deletion_reason fields")

def check_url_patterns():
    """URL 패턴 검증"""
    print("\n🔍 Checking URL patterns...")
    
    from django.urls import get_resolver
    resolver = get_resolver()
    
    # 주요 API 엔드포인트 확인
    endpoints = [
        '/api/auth/login/',
        '/api/auth/signup/',
        '/api/version/',
        '/api/system/version/',
        '/api/health/',
    ]
    
    for endpoint in endpoints:
        try:
            match = resolver.resolve(endpoint)
            print(f"✅ {endpoint} -> {match.func.__module__}.{match.func.__name__}")
        except Exception as e:
            print(f"❌ {endpoint} -> Not found: {e}")

def run_migrations():
    """마이그레이션 실행"""
    print("\n🚀 Running migrations...")
    
    try:
        call_command('migrate', '--no-input')
        print("✅ Migrations completed successfully")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    return True

def create_test_user():
    """테스트 사용자 생성"""
    print("\n👤 Creating test user...")
    
    from users.models import User
    
    try:
        # 기존 테스트 사용자 삭제
        User.objects.filter(email='railway_test@example.com').delete()
        
        # 새 테스트 사용자 생성
        user = User.objects.create_user(
            username='railway_test@example.com',
            email='railway_test@example.com',
            password='RailwayTest123!',
            nickname='Railway Test User',
            deletion_reason=''  # 명시적으로 설정
        )
        user.email_verified = True
        user.save()
        
        print(f"✅ Test user created: {user.email}")
        return user
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

def test_login_api():
    """로그인 API 테스트"""
    print("\n🧪 Testing login API...")
    
    import json
    from django.test import Client
    
    client = Client()
    
    # 로그인 테스트
    response = client.post(
        '/api/auth/login/',
        data=json.dumps({
            'email': 'railway_test@example.com',
            'password': 'RailwayTest123!'
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        print(f"✅ Login successful: {response.status_code}")
        data = response.json()
        if 'access' in data:
            print(f"   Token received: {data['access'][:50]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("백엔드 API 오류 수정 스크립트")
    print("=" * 60)
    
    # 1. 데이터베이스 문제 수정
    fix_deletion_reason_field()
    
    # 2. 마이그레이션 실행
    if run_migrations():
        # 3. URL 패턴 확인
        check_url_patterns()
        
        # 4. 테스트 사용자 생성
        if create_test_user():
            # 5. API 테스트
            test_login_api()
    
    print("\n" + "=" * 60)
    print("스크립트 실행 완료")
    print("=" * 60)

if __name__ == '__main__':
    main()