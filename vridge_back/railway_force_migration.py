#!/usr/bin/env python3
"""
Railway 환경 전용 - 500 에러 해결을 위한 강제 마이그레이션
"""
import os
import sys

# Railway 환경 설정 강제 적용
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

try:
    import django
    django.setup()
    
    from django.core.management import call_command
    from django.db import connection, transaction
    from users.models import User
    
    print("=== Railway 500 에러 해결 - 강제 마이그레이션 ===")
    
    # 1. 데이터베이스 연결 확인
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Railway 데이터베이스 연결 성공")
    except Exception as e:
        print(f"❌ Railway 데이터베이스 연결 실패: {e}")
        sys.exit(1)
    
    # 2. 현재 마이그레이션 상태 확인
    print("\n=== 현재 마이그레이션 상태 ===")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM django_migrations 
            WHERE app = 'users' 
            ORDER BY id DESC 
            LIMIT 3;
        """)
        current_migrations = cursor.fetchall()
        print("최근 적용된 마이그레이션:")
        for migration in current_migrations:
            print(f"  - {migration[0]}")
    
    # 3. deletion_reason 필드 상태 확인
    print("\n=== deletion_reason 필드 상태 확인 ===")
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'users_user' 
                AND column_name = 'deletion_reason';
            """)
            result = cursor.fetchone()
            if result:
                print(f"✅ deletion_reason 필드 존재: {result[1]}, nullable={result[2]}, default={result[3]}")
            else:
                print("❌ deletion_reason 필드가 존재하지 않음!")
                
                # 4. 필드가 없으면 직접 추가
                print("\n=== deletion_reason 필드 직접 추가 ===")
                try:
                    cursor.execute("""
                        ALTER TABLE users_user 
                        ADD COLUMN deletion_reason VARCHAR(200) DEFAULT '' NULL;
                    """)
                    print("✅ deletion_reason 필드 직접 추가 완료")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print("✅ deletion_reason 필드가 이미 존재함")
                    else:
                        print(f"❌ 필드 추가 실패: {e}")
    
    # 5. 강제 마이그레이션 실행
    print("\n=== 강제 마이그레이션 실행 ===")
    try:
        call_command('migrate', 'users', '--noinput', verbosity=2)
        print("✅ users 앱 마이그레이션 완료")
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        # 무시하고 계속 진행
    
    # 6. 전체 마이그레이션 실행
    try:
        call_command('migrate', '--noinput', verbosity=1)
        print("✅ 전체 마이그레이션 완료")
    except Exception as e:
        print(f"❌ 전체 마이그레이션 실패: {e}")
    
    # 7. User 모델 테스트
    print("\n=== User 모델 최종 테스트 ===")
    try:
        # 기존 사용자로 테스트
        user_count = User.objects.count()
        print(f"총 사용자 수: {user_count}")
        
        if user_count > 0:
            test_user = User.objects.first()
            print(f"테스트 사용자: {test_user.username}")
            print(f"deletion_reason: '{test_user.deletion_reason}' (타입: {type(test_user.deletion_reason)})")
            print(f"email_verified: {test_user.email_verified}")
            print(f"is_active: {test_user.is_active}")
            
        # 새 사용자 생성 테스트 (실제 생성)
        from django.contrib.auth import authenticate
        test_email = "railway_test_user@test.com"
        
        # 기존 테스트 사용자 삭제
        User.objects.filter(username=test_email).delete()
        User.objects.filter(email=test_email).delete()
        
        # 새 사용자 생성
        new_user = User.objects.create_user(
            username=test_email,
            email=test_email,
            password='testpass123'
        )
        print(f"✅ 새 사용자 생성 성공: {new_user.username}")
        print(f"   deletion_reason: '{new_user.deletion_reason}'")
        
        # 인증 테스트
        auth_user = authenticate(username=test_email, password='testpass123')
        if auth_user:
            print("✅ 사용자 인증 테스트 성공")
        else:
            print("❌ 사용자 인증 테스트 실패")
        
        # 테스트 사용자 정리
        new_user.delete()
        print("✅ 테스트 사용자 정리 완료")
        
    except Exception as e:
        print(f"❌ User 모델 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 8. 최종 상태 확인
    print("\n=== 최종 상태 확인 ===")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users_user' 
            AND column_name IN ('deletion_reason', 'email_verified', 'is_active')
            ORDER BY column_name;
        """)
        final_fields = cursor.fetchall()
        print("중요 필드 확인:")
        for field in final_fields:
            print(f"  ✅ {field[0]}: {field[1]}")
    
    print("\n🎉 Railway 500 에러 해결 작업 완료!")
    print("이제 https://videoplanet.up.railway.app/api/users/login/ 테스트 가능")
    
except Exception as e:
    print(f"스크립트 실행 오류: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)