#!/usr/bin/env python
"""
Railway 데이터베이스 긴급 수정 스크립트
deletion_reason 필드 문제를 해결합니다.
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

# Django 초기화
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def fix_database():
    """데이터베이스 스키마 수정"""
    
    print("=" * 60)
    print("Railway Database Fix Script")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        try:
            # 1. 테이블 존재 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users_user'
                AND column_name = 'deletion_reason'
            """)
            
            result = cursor.fetchone()
            
            if result:
                print(f"✓ deletion_reason field exists")
                print(f"  - Type: {result[1]}")
                print(f"  - Nullable: {result[2]}")
                print(f"  - Default: {result[3]}")
                
                # 기본값이 없으면 추가
                if result[3] is None:
                    print("\n⚠ No default value set. Adding default...")
                    cursor.execute("""
                        ALTER TABLE users_user 
                        ALTER COLUMN deletion_reason 
                        SET DEFAULT ''
                    """)
                    print("✓ Default value added")
                
                # NULL 값을 빈 문자열로 업데이트
                cursor.execute("""
                    UPDATE users_user 
                    SET deletion_reason = '' 
                    WHERE deletion_reason IS NULL
                """)
                updated = cursor.rowcount
                print(f"✓ Updated {updated} NULL values to empty string")
                
            else:
                print("⚠ deletion_reason field not found. Creating...")
                cursor.execute("""
                    ALTER TABLE users_user 
                    ADD COLUMN deletion_reason VARCHAR(200) DEFAULT '' NOT NULL
                """)
                print("✓ deletion_reason field created")
            
            # 2. 다른 필수 필드들도 확인
            required_fields = [
                ('email_verified', 'BOOLEAN', 'FALSE'),
                ('is_deleted', 'BOOLEAN', 'FALSE'),
                ('can_recover', 'BOOLEAN', 'TRUE'),
            ]
            
            for field_name, field_type, default_value in required_fields:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns
                    WHERE table_name = 'users_user'
                    AND column_name = '{field_name}'
                """)
                
                if not cursor.fetchone():
                    print(f"\n⚠ {field_name} field not found. Creating...")
                    cursor.execute(f"""
                        ALTER TABLE users_user 
                        ADD COLUMN {field_name} {field_type} DEFAULT {default_value}
                    """)
                    print(f"✓ {field_name} field created")
            
            # 3. 커밋
            connection.commit()
            print("\n✅ Database schema fixed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            connection.rollback()
            
            # Fallback: 마이그레이션 fake 적용
            print("\nTrying migration fake...")
            try:
                execute_from_command_line(['manage.py', 'migrate', 'users', '--fake'])
                print("✅ Migration fake applied")
            except Exception as e2:
                print(f"❌ Migration fake failed: {e2}")

if __name__ == "__main__":
    fix_database()