#!/usr/bin/env python3
"""
Railway   
"""
import os
import sys

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_safe')

try:
    import django
    django.setup()
    
    from django.core.management import call_command
    from django.db import connection
    
    print(" Railway  ...")
    
    #   
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("   ")
    except Exception as e:
        print(f"   : {e}")
        sys.exit(1)
    
    #  
    print("   ...")
    call_command('migrate', '--noinput')
    print("  ")
    
    #  
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users_notification'
                );
            """)
            notification_exists = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'users_user' 
                    AND column_name = 'email_verified'
                );
            """)
            email_verified_exists = cursor.fetchone()[0]
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users_notification';")
            notification_exists = bool(cursor.fetchone())
            
            cursor.execute("PRAGMA table_info(users_user);")
            columns = [row[1] for row in cursor.fetchall()]
            email_verified_exists = 'email_verified' in columns
        
        print(f"  :")
        print(f"   users_notification: {'' if notification_exists else ''}")
        print(f"   email_verified : {'' if email_verified_exists else ''}")
    
    print(" Railway  !")
    
except Exception as e:
    print(f"  : {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)