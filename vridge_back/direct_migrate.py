#!/usr/bin/env python3
"""
Railway    
"""
import os
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_minimal')
django.setup()

from django.db import connection
from django.core.management import call_command

print("   ...")

def execute_sql_safely(sql, description):
    """SQL  """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            print(f" {description}")
            return True
    except Exception as e:
        print(f" {description} -   : {e}")
        return False

def is_postgresql():
    """PostgreSQL """
    return connection.vendor == 'postgresql'

# PostgreSQL  SQL 
if is_postgresql():
    print(" PostgreSQL  -  SQL ...")
    
    # 1. users_notification  
    execute_sql_safely("""
        CREATE TABLE IF NOT EXISTS users_notification (
            id SERIAL PRIMARY KEY,
            created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            recipient_id INTEGER NOT NULL,
            notification_type VARCHAR(50) NOT NULL,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            project_id INTEGER,
            invitation_id INTEGER,
            is_read BOOLEAN DEFAULT FALSE,
            read_at TIMESTAMP WITH TIME ZONE,
            extra_data JSONB DEFAULT '{}'::jsonb
        );
    """, "users_notification  ")

    # 2.  
    execute_sql_safely(
        "CREATE INDEX IF NOT EXISTS users_notification_recipient_created ON users_notification(recipient_id, created DESC);",
        "users_notification  "
    )

    # 3. email_verified  
    execute_sql_safely(
        "ALTER TABLE users_user ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;",
        "email_verified  "
    )

    # 4. email_verified_at  
    execute_sql_safely(
        "ALTER TABLE users_user ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE;",
        "email_verified_at  "
    )

    # 5. friend_code  
    execute_sql_safely(
        "ALTER TABLE users_user ADD COLUMN IF NOT EXISTS friend_code VARCHAR(20) UNIQUE;",
        "friend_code  "
    )
else:
    print(" SQLite  -  SQL    ...")

# 6.   
print("\n   ...")
try:
    call_command('migrate', '--noinput')
    print("   ")
except Exception as e:
    print(f"   : {e}")

print("\n   !")