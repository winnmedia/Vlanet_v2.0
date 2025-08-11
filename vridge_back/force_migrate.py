#\!/usr/bin/env python
"""
  
Railway    
"""
import os
import sys
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

def main():
    print("===    ===")
    
    #   
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"  : {len(tables)}")
        
    #  
    try:
        print("\n1. contenttypes ...")
        execute_from_command_line(['manage.py', 'migrate', 'contenttypes', '--noinput'])
        
        print("\n2. auth ...")
        execute_from_command_line(['manage.py', 'migrate', 'auth', '--noinput'])
        
        print("\n3. users ...")
        execute_from_command_line(['manage.py', 'migrate', 'users', '--noinput'])
        
        print("\n4. projects ...")
        execute_from_command_line(['manage.py', 'migrate', 'projects', '--noinput'])
        
        print("\n5.   ...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        print("\n===   ===")
        
        #    
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"   : {len(tables)}")
            
            # projects_developmentframework  
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'projects_developmentframework'
                );
            """)
            exists = cursor.fetchone()[0]
            if exists:
                print(" projects_developmentframework  ")
            else:
                print(" projects_developmentframework   ")
                
    except Exception as e:
        print(f" : {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
