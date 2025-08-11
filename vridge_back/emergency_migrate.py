"""
Railway 환경 is_deleted 필드 응급 복구 스크립트
Django 마이그레이션이 실패했을 때 수동으로 필드를 추가하는 스크립트
사용법: python emergency_migrate.py
"""
import os
import sys
import django
from django.core.management import call_command
from django.db import connection, transaction

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

def emergency_add_is_deleted_fields():
    """응급 상황에서 is_deleted 관련 필드들을 수동으로 추가"""
    print("=== is_deleted 필드 응급 복구 시작 ===")
    
    try:
        with connection.cursor() as cursor:
            # 1. 현재 users_user 테이블 구조 확인
            print("\n1. 현재 users_user 테이블 컬럼 확인:")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name='users_user' 
                AND column_name IN ('is_deleted', 'deleted_at', 'can_recover', 'deletion_reason', 'recovery_deadline')
                ORDER BY column_name;
            """)
            existing_columns = cursor.fetchall()
            existing_column_names = {col[0] for col in existing_columns}
            
            print("기존 필드:")
            for col in existing_columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'} DEFAULT {col[3] or 'None'}")
            
            # 2. 부족한 필드 추가
            required_fields = {
                'is_deleted': "BOOLEAN DEFAULT FALSE NOT NULL",
                'deleted_at': "TIMESTAMP NULL",
                'can_recover': "BOOLEAN DEFAULT TRUE NOT NULL", 
                'deletion_reason': "VARCHAR(200) NULL",
                'recovery_deadline': "TIMESTAMP NULL"
            }
            
            print("\n2. 부족한 필드 추가 중...")
            with transaction.atomic():
                for field_name, field_def in required_fields.items():
                    if field_name not in existing_column_names:
                        sql = f"ALTER TABLE users_user ADD COLUMN {field_name} {field_def}"
                        print(f"  실행: {sql}")
                        cursor.execute(sql)
                        print(f"  ✓ {field_name} 필드 추가 완료")
                    else:
                        print(f"  ⚠ {field_name} 필드 이미 존재")
                        
                # 3. 인덱스 추가
                print("\n3. 인덱스 추가 중...")
                index_sql = """
                    CREATE INDEX IF NOT EXISTS users_user_is_deleted_deleted_at_idx 
                    ON users_user (is_deleted, deleted_at)
                """
                cursor.execute(index_sql)
                print("  ✓ 인덱스 추가 완료")
                
        return True
        
    except Exception as e:
        print(f"\n❌ 필드 추가 실패: {str(e)}")
        return False

def verify_is_deleted_fields():
    """필드 추가 후 ORM 접근 테스트"""
    print("\n4. ORM 접근 테스트:")
    
    try:
        from users.models import User
        
        # ORM으로 테스트 쿼리 실행
        total_users = User.objects.count()
        active_users = User.objects.filter(is_deleted=False).count() 
        deleted_users = User.objects.filter(is_deleted=True).count()
        
        print(f"  - 총 사용자 수: {total_users}")
        print(f"  - 활성 사용자 수 (is_deleted=False): {active_users}")
        print(f"  - 삭제된 사용자 수 (is_deleted=True): {deleted_users}")
        
        # 직접 SQL로도 검증
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users_user WHERE is_deleted = FALSE")
            sql_count = cursor.fetchone()[0]
            print(f"  - SQL 직접 쿼리 결과: {sql_count}")
            
        print("  ✓ ORM 접근 테스트 성공")
        return True
        
    except Exception as e:
        print(f"  ❌ ORM 접근 테스트 실패: {str(e)}")
        return False

def run_emergency_migration():
    """전체 응급 복구 프로세스 실행"""
    success_steps = 0
    total_steps = 3
    
    # Step 1: 필드 추가
    if emergency_add_is_deleted_fields():
        success_steps += 1
    else:
        print("필드 추가 단계에서 실패했습니다.")
        return False
        
    # Step 2: ORM 테스트
    if verify_is_deleted_fields():
        success_steps += 1
    else:
        print("ORM 테스트 단계에서 실패했습니다.")
        
    # Step 3: Django 마이그레이션 상태 동기화 시도
    print("\n5. Django 마이그레이션 상태 동기화:")
    try:
        call_command('migrate', '--fake', 'users', '0016', verbosity=2)
        call_command('migrate', '--fake', 'users', '0017', verbosity=2)
        call_command('migrate', '--fake', 'users', '0018', verbosity=2)
        print("  ✓ 마이그레이션 상태 동기화 완료")
        success_steps += 1
    except Exception as e:
        print(f"  ⚠ 마이그레이션 상태 동기화 실패 (무시 가능): {str(e)}")
        
    print(f"\n=== 응급 복구 완료 ({success_steps}/{total_steps} 단계 성공) ===")
    
    if success_steps >= 2:  # 필드 추가와 ORM 테스트만 성공하면 OK
        print("✅ is_deleted 필드 복구가 성공적으로 완료되었습니다!")
        print("이제 Django 서버를 다시 시작할 수 있습니다.")
        return True
    else:
        print("❌ 복구에 실패했습니다. 수동 데이터베이스 작업이 필요할 수 있습니다.")
        return False

if __name__ == "__main__":
    print("VideoPlanet Railway is_deleted 필드 응급 복구 스크립트")
    print("=" * 60)
    
    success = run_emergency_migration()
    
    if success:
        print("\n🎉 복구 성공! Railway에서 서버를 다시 시작해주세요.")
        sys.exit(0)
    else:
        print("\n💥 복구 실패. Railway 로그를 확인하고 데이터베이스 상태를 점검해주세요.")
        sys.exit(1)