#!/usr/bin/env python3
"""
Railway     
"""
import os
import sys
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_safe')
django.setup()

from django.db import connection
from django.core.management import call_command

def check_table_exists(table_name):
    """   """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def main():
    print(" Railway    ...")
    print(f"DATABASE: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")
    
    #   
    tables_to_check = [
        'projects_project',
        'projects_projectinvitation',
        'projects_projectinvite',
        'projects_members',
        'users_user',
        'users_userprofile',
        'django_migrations'
    ]
    
    print("\n   :")
    for table in tables_to_check:
        exists = check_table_exists(table)
        status = " " if exists else " "
        print(f"   {table}: {status}")
    
    #   
    print("\n   :")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT app, name, applied 
            FROM django_migrations 
            WHERE app IN ('projects', 'users')
            ORDER BY applied DESC 
            LIMIT 10
        """)
        for row in cursor.fetchall():
            app, name, applied = row
            print(f"   [{app}] {name} - {applied}")
    
    # ProjectInvitation     
    if not check_table_exists('projects_projectinvitation'):
        print("\n  ProjectInvitation  !")
        print("  :")
        print("python manage.py migrate projects")
    else:
        print("\n    .")

if __name__ == "__main__":
    main()