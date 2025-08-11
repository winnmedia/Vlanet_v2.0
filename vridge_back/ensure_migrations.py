#!/usr/bin/env python3
"""
Railway       
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

def check_database():
    """  """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print(" Database connection successful")
        return True
    except Exception as e:
        print(f" Database connection failed: {e}")
        return False

def run_migrations():
    """ """
    try:
        print(" Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print(" Migrations completed successfully")
        return True
    except Exception as e:
        print(f" Migration failed: {e}")
        return False

def main():
    """ """
    # Django 
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
    
    try:
        django.setup()
        
        print(" Checking database connection...")
        if not check_database():
            sys.exit(1)
        
        print(" Running migrations...")
        if not run_migrations():
            sys.exit(1)
            
        print(" All operations completed successfully!")
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()