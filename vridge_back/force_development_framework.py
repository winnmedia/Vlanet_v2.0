#!/usr/bin/env python
"""
development_framework    
"""
import os
import sys
import django
from django.db import connection, transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

def add_development_framework_column():
    """development_framework_id  """
    with connection.cursor() as cursor:
        try:
            #    
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'projects_project' 
                AND column_name = 'development_framework_id'
            """)
            
            if cursor.fetchone():
                print(" development_framework_id   .")
                return
            
            #  
            print(" development_framework_id  ...")
            with transaction.atomic():
                cursor.execute("""
                    ALTER TABLE projects_project 
                    ADD COLUMN development_framework_id INTEGER NULL
                    REFERENCES projects_developmentframework(id) 
                    ON DELETE SET NULL 
                    DEFERRABLE INITIALLY DEFERRED
                """)
                
                #  
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS projects_project_development_framework_id_idx 
                    ON projects_project(development_framework_id)
                """)
                
            print(" development_framework_id   .")
            
        except Exception as e:
            print(f"     : {str(e)}")
            raise

if __name__ == "__main__":
    print("=== Development Framework    ===")
    add_development_framework_column()
    print("===  ===")