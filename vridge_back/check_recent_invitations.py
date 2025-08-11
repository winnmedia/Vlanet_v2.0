#!/usr/bin/env python
"""
RecentInvitation   
Railway     
"""
import os
import sys
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from users.models import RecentInvitation

print("=== RecentInvitation   ===")

#   
db_engine = connection.settings_dict['ENGINE']
print(f"\n1.  : {db_engine}")

# PostgreSQL 
if 'postgresql' in db_engine:
    with connection.cursor() as cursor:
        #   
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users_recentinvitation'
            );
        """)
        table_exists = cursor.fetchone()[0]
        print(f"2.  : {table_exists}")
        
        if table_exists:
            #  
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'users_recentinvitation'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("\n3.  :")
            for col_name, col_type in columns:
                print(f"  - {col_name}: {col_type}")
                
            #   
            cursor.execute("SELECT COUNT(*) FROM users_recentinvitation;")
            count = cursor.fetchone()[0]
            print(f"\n4.   : {count}")
        else:
            print("\n users_recentinvitation   !")
            print("    : python manage.py migrate users")

# SQLite 
elif 'sqlite' in db_engine:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users_recentinvitation';
        """)
        result = cursor.fetchone()
        print(f"2.  : {result is not None}")

print("\n===    ===")
try:
    from django.db.migrations.recorder import MigrationRecorder
    recorder = MigrationRecorder(connection)
    applied_migrations = recorder.applied_migrations()
    
    users_migrations = [m for m in applied_migrations if m[0] == 'users']
    print(f" users  : {len(users_migrations)}")
    
    # 0012  
    has_0012 = ('users', '0012_recentinvitation_friendship') in applied_migrations
    print(f"0012_recentinvitation_friendship  : {has_0012}")
    
except Exception as e:
    print(f"  : {e}")