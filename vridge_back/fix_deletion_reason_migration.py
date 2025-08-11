#!/usr/bin/env python
"""
Fix deletion_reason field migration conflicts
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

from django.db import connection, migrations
from django.core.management import call_command

def fix_deletion_reason_field():
    """Fix the deletion_reason field issues"""
    
    with connection.cursor() as cursor:
        # 1. Check current state
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users_user' 
            AND column_name = 'deletion_reason';
        """)
        
        result = cursor.fetchone()
        
        if result:
            print(f"Current deletion_reason field: {result}")
            
            # 2. Update existing NULL values
            cursor.execute("""
                UPDATE users_user 
                SET deletion_reason = '' 
                WHERE deletion_reason IS NULL;
            """)
            
            affected = cursor.rowcount
            print(f"Updated {affected} rows with NULL deletion_reason")
            
            # 3. Add default constraint if missing
            try:
                cursor.execute("""
                    ALTER TABLE users_user 
                    ALTER COLUMN deletion_reason 
                    SET DEFAULT '';
                """)
                print("Default constraint added")
            except Exception as e:
                print(f"Default constraint may already exist: {e}")
        else:
            print("deletion_reason field not found - migrations may need to run")
            
            # Try to run migrations
            try:
                call_command('migrate', 'users', verbosity=2)
            except Exception as e:
                print(f"Migration error: {e}")
                
                # Force create the field if needed
                cursor.execute("""
                    ALTER TABLE users_user 
                    ADD COLUMN IF NOT EXISTS deletion_reason 
                    VARCHAR(200) DEFAULT '' NULL;
                """)
                print("Field created manually")

if __name__ == '__main__':
    fix_deletion_reason_field()
    print("Fix completed")