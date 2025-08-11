#!/usr/bin/env python
"""
Railway    
"""
import os
import sys
import django
from django.core.management import call_command

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

print("     ...")

try:
    # 1.    
    print("\n   :")
    call_command('showmigrations', 'users')
    
    # 2. users   
    print("\n users   :")
    call_command('migrate', 'users', '--noinput')
    
    # 3.    
    print("\n   :")
    call_command('migrate', '--noinput')
    
    # 4.   
    from django.db import connection
    with connection.cursor() as cursor:
        # users_notification  
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users_notification'
            );
        """)
        notification_exists = cursor.fetchone()[0]
        
        # email_verified  
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'users_user' 
                AND column_name = 'email_verified'
            );
        """)
        email_verified_exists = cursor.fetchone()[0]
        
        print(f"\n users_notification : {'' if notification_exists else ' '}")
        print(f" email_verified : {'' if email_verified_exists else ' '}")
    
    print("\n  !")
    
except Exception as e:
    print(f"\n  : {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)