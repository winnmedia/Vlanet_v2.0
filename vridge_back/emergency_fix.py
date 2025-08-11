#!/usr/bin/env python
"""
   
"""
import os
import sys
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

def emergency_fix():
    """ """
    with connection.cursor() as cursor:
        try:
            # 1. development_framework_id   
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'projects_project' 
                AND column_name = 'development_framework_id'
            """)
            
            if not cursor.fetchone():
                print(" development_framework_id  .")
                #   
                try:
                    cursor.execute("""
                        ALTER TABLE projects_project 
                        ADD COLUMN development_framework_id INTEGER NULL
                    """)
                    print(" development_framework_id  .")
                except Exception as e:
                    print(f"   : {str(e)}")
            else:
                print(" development_framework_id   .")
            
            # 2.  
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'projects_developmentframework'
            """)
            
            if not cursor.fetchone():
                print(" projects_developmentframework  .")
            else:
                print(" projects_developmentframework  .")
                
        except Exception as e:
            print(f"    : {str(e)}")

if __name__ == "__main__":
    print("===     ===")
    emergency_fix()
    print("===  ===")