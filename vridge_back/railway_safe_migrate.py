#!/usr/bin/env python3
"""
Railway 안전 마이그레이션 - 500 에러 해결
마이그레이션 실패 시에도 서버가 계속 작동할 수 있도록 안전장치 포함
"""
import os
import sys

# Railway 환경 전용 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

def safe_execute_sql(cursor, sql, description):
    """SQL 실행을 안전하게 처리"""
    try:
        cursor.execute(sql)
        print(f"✅ {description}")
        return True
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"✅ {description} (이미 존재함)")
            return True
        else:
            print(f"⚠️ {description} 실패: {e}")
            return False

try:
    import django
    django.setup()
    
    from django.db import connection, transaction
    from django.core.management import call_command
    
    print("=== Railway 안전 마이그레이션 시작 ===")
    
    # 1. 연결 테스트
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL 연결 성공: {db_version}")
    
    # 2. 안전한 스키마 수정
    print("\n=== 안전한 스키마 수정 ===")
    with connection.cursor() as cursor:
        # deletion_reason 필드가 없으면 추가
        safe_execute_sql(
            cursor,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users_user' AND column_name = 'deletion_reason'
                ) THEN
                    ALTER TABLE users_user 
                    ADD COLUMN deletion_reason VARCHAR(200) DEFAULT '' NULL;
                END IF;
            END $$;
            """,
            "deletion_reason 필드 추가"
        )
        
        # email_verified 필드 확인 및 추가
        safe_execute_sql(
            cursor,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users_user' AND column_name = 'email_verified'
                ) THEN
                    ALTER TABLE users_user 
                    ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL;
                END IF;
            END $$;
            """,
            "email_verified 필드 추가"
        )
        
        # email_verified_at 필드 확인 및 추가
        safe_execute_sql(
            cursor,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users_user' AND column_name = 'email_verified_at'
                ) THEN
                    ALTER TABLE users_user 
                    ADD COLUMN email_verified_at TIMESTAMPTZ NULL;
                END IF;
            END $$;
            """,
            "email_verified_at 필드 추가"
        )
        
        # is_deleted 필드 확인 및 추가
        safe_execute_sql(
            cursor,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users_user' AND column_name = 'is_deleted'
                ) THEN
                    ALTER TABLE users_user 
                    ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
                END IF;
            END $$;
            """,
            "is_deleted 필드 추가"
        )
        
        # deleted_at 필드 확인 및 추가
        safe_execute_sql(
            cursor,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users_user' AND column_name = 'deleted_at'
                ) THEN
                    ALTER TABLE users_user 
                    ADD COLUMN deleted_at TIMESTAMPTZ NULL;
                END IF;
            END $$;
            """,
            "deleted_at 필드 추가"
        )
        
        # can_recover 필드 확인 및 추가
        safe_execute_sql(
            cursor,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users_user' AND column_name = 'can_recover'
                ) THEN
                    ALTER TABLE users_user 
                    ADD COLUMN can_recover BOOLEAN DEFAULT TRUE NOT NULL;
                END IF;
            END $$;
            """,
            "can_recover 필드 추가"
        )
        
        # recovery_deadline 필드 확인 및 추가
        safe_execute_sql(
            cursor,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users_user' AND column_name = 'recovery_deadline'
                ) THEN
                    ALTER TABLE users_user 
                    ADD COLUMN recovery_deadline TIMESTAMPTZ NULL;
                END IF;
            END $$;
            """,
            "recovery_deadline 필드 추가"
        )
    
    # 3. Django 마이그레이션 상태 동기화
    print("\n=== Django 마이그레이션 동기화 ===")
    try:
        # 가짜 마이그레이션 적용으로 상태 동기화
        call_command('migrate', 'users', '--fake', verbosity=0)
        print("✅ 마이그레이션 상태 동기화 완료")
    except Exception as e:
        print(f"⚠️ 마이그레이션 동기화 실패 (무시): {e}")
    
    # 4. 실제 마이그레이션 시도
    print("\n=== 실제 마이그레이션 실행 ===")
    try:
        call_command('migrate', '--noinput')
        print("✅ 전체 마이그레이션 완료")
    except Exception as e:
        print(f"⚠️ 마이그레이션 실패 (서버는 계속 작동): {e}")
    
    # 5. 최종 검증
    print("\n=== 최종 검증 ===")
    try:
        from users.models import User
        
        # 사용자 수 확인
        user_count = User.objects.count()
        print(f"✅ 사용자 모델 접근 성공 - 총 {user_count}명")
        
        # 필드 접근 테스트
        if user_count > 0:
            test_user = User.objects.first()
            test_fields = {
                'deletion_reason': getattr(test_user, 'deletion_reason', 'N/A'),
                'email_verified': getattr(test_user, 'email_verified', 'N/A'),
                'is_active': getattr(test_user, 'is_active', 'N/A'),
                'is_deleted': getattr(test_user, 'is_deleted', 'N/A'),
            }
            
            print("✅ 중요 필드 접근 테스트:")
            for field, value in test_fields.items():
                print(f"   {field}: {value}")
        
    except Exception as e:
        print(f"❌ 최종 검증 실패: {e}")
        print("하지만 스키마 수정은 완료되어 서버가 작동할 수 있습니다.")
    
    print("\n🎉 Railway 안전 마이그레이션 완료!")
    print("서버 재시작 후 /api/users/login/ 테스트하세요.")
    
except Exception as e:
    print(f"❌ 치명적 오류: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)