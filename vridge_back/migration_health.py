#!/usr/bin/env python3
"""
Railway      
"""
import os
import sys

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

try:
    import django
    django.setup()
    
    from django.core.management import call_command
    from django.db import connection
    
    print("   ...")
    print(f"DATABASE: {connection.vendor}")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")
    
    # 1.   
    print("\n   :")
    call_command('showmigrations')
    
    # 2.  
    print("\n  :")
    call_command('migrate', '--noinput')
    
    # 3.   
    with connection.cursor() as cursor:
        # users_notification  
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users_notification'
                );
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users_notification';
            """)
        
        result = cursor.fetchone()
        notification_exists = result[0] if result else False
        
        # email_verified  
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'users_user' 
                    AND column_name = 'email_verified'
                );
            """)
        else:
            cursor.execute("PRAGMA table_info(users_user);")
            columns = [row[1] for row in cursor.fetchall()]
            email_verified_exists = 'email_verified' in columns
        
        if connection.vendor == 'postgresql':
            result = cursor.fetchone()
            email_verified_exists = result[0] if result else False
        
        print(f"\n  :")
        print(f"   users_notification: {' ' if notification_exists else ' '}")
        print(f"   email_verified : {' ' if email_verified_exists else ' '}")
    
    print("\n   !")
    
except Exception as e:
    print(f"\n  : {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)