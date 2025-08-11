#!/usr/bin/env python3
"""
Railway 데이터베이스 상태 진단 및 마이그레이션 문제 해결
"""
import os
import sys

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

try:
    import django
    django.setup()
    
    from django.core.management import call_command
    from django.db import connection
    from users.models import User
    
    print("=== Railway 데이터베이스 진단 ===")
    
    # 1. 데이터베이스 연결 테스트
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ 데이터베이스 연결 성공")
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        sys.exit(1)
    
    # 2. users_user 테이블 구조 확인
    print("\n=== users_user 테이블 구조 확인 ===")
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default 
                    FROM information_schema.columns 
                    WHERE table_name = 'users_user' 
                    AND table_schema = 'public'
                    ORDER BY column_name;
                """)
                columns = cursor.fetchall()
                print("컬럼 정보:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}, nullable={col[2]}, default={col[3]}")
                
                # deletion_reason 필드 특별 확인
                deletion_reason_exists = any(col[0] == 'deletion_reason' for col in columns)
                print(f"\n🔍 deletion_reason 필드 존재 여부: {'✅ 존재' if deletion_reason_exists else '❌ 없음'}")
                
                if deletion_reason_exists:
                    deletion_info = next((col for col in columns if col[0] == 'deletion_reason'), None)
                    print(f"   타입: {deletion_info[1]}, nullable: {deletion_info[2]}, default: {deletion_info[3]}")
            
    except Exception as e:
        print(f"❌ 테이블 구조 확인 실패: {e}")
    
    # 3. 마이그레이션 상태 확인
    print("\n=== 마이그레이션 상태 확인 ===")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app, name 
                FROM django_migrations 
                WHERE app = 'users' 
                ORDER BY id DESC 
                LIMIT 5;
            """)
            migrations = cursor.fetchall()
            print("최근 적용된 users 앱 마이그레이션:")
            for migration in migrations:
                print(f"  - {migration[0]}: {migration[1]}")
            
            # 특정 마이그레이션 확인
            cursor.execute("""
                SELECT COUNT(*) 
                FROM django_migrations 
                WHERE app = 'users' AND name = '0019_alter_user_deletion_reason_default';
            """)
            migration_0019_applied = cursor.fetchone()[0] > 0
            print(f"\n🔍 0019_alter_user_deletion_reason_default 적용 여부: {'✅ 적용됨' if migration_0019_applied else '❌ 미적용'}")
            
    except Exception as e:
        print(f"❌ 마이그레이션 상태 확인 실패: {e}")
    
    # 4. User 모델 테스트
    print("\n=== User 모델 테스트 ===")
    try:
        # 사용자 수 확인
        user_count = User.objects.count()
        print(f"총 사용자 수: {user_count}")
        
        # deletion_reason 필드 직접 테스트
        if user_count > 0:
            test_user = User.objects.first()
            print(f"테스트 사용자: {test_user.username}")
            print(f"deletion_reason 값: '{test_user.deletion_reason}'")
            print(f"deletion_reason 타입: {type(test_user.deletion_reason)}")
        
        # 새 사용자 생성 테스트 (실제로는 생성하지 않음)
        print("\n새 사용자 생성 테스트 (롤백)...")
        from django.db import transaction
        with transaction.atomic():
            test_user = User.objects.create_user(
                username='test_railway_user',
                email='test@railway.com',
                password='testpassword123'
            )
            print(f"✅ 사용자 생성 성공 - deletion_reason: '{test_user.deletion_reason}'")
            # 롤백을 위해 예외 발생
            raise Exception("테스트 완료 - 롤백")
            
    except Exception as e:
        if "테스트 완료" in str(e):
            print("✅ 사용자 생성 테스트 완료 (롤백됨)")
        else:
            print(f"❌ User 모델 테스트 실패: {e}")
    
    # 5. 로그인 테스트 시뮬레이션
    print("\n=== 로그인 테스트 시뮬레이션 ===")
    try:
        if User.objects.count() > 0:
            test_user = User.objects.first()
            # 필드 접근 테스트
            fields_to_test = ['email_verified', 'is_active', 'deletion_reason', 'login_method']
            for field in fields_to_test:
                try:
                    value = getattr(test_user, field, 'NOT_FOUND')
                    print(f"  - {field}: {value} ({type(value)})")
                except Exception as field_error:
                    print(f"  - {field}: ❌ 접근 실패 - {field_error}")
        else:
            print("테스트할 사용자가 없습니다.")
            
    except Exception as e:
        print(f"❌ 로그인 테스트 실패: {e}")
    
    print("\n=== 진단 완료 ===")
    
except Exception as e:
    print(f"스크립트 실행 오류: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)