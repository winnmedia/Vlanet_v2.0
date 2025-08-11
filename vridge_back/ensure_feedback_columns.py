#!/usr/bin/env python
"""
  display_mode nickname   
  
"""
import os
import sys
import django
from django.db import connection

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

def ensure_feedback_columns():
    """      """
    with connection.cursor() as cursor:
        # 1.    
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'feedbacks_feedbackcomment' 
            AND column_name IN ('display_mode', 'nickname')
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # 2. display_mode   
        if 'display_mode' not in existing_columns:
            print("Adding display_mode column...")
            try:
                cursor.execute("""
                    ALTER TABLE feedbacks_feedbackcomment 
                    ADD COLUMN display_mode VARCHAR(20) DEFAULT 'anonymous'
                """)
                print(" display_mode column added successfully")
            except Exception as e:
                print(f" Failed to add display_mode column: {e}")
        
        # 3. nickname   
        if 'nickname' not in existing_columns:
            print("Adding nickname column...")
            try:
                cursor.execute("""
                    ALTER TABLE feedbacks_feedbackcomment 
                    ADD COLUMN nickname VARCHAR(20) NULL
                """)
                print(" nickname column added successfully")
            except Exception as e:
                print(f" Failed to add nickname column: {e}")
        
        # 4.  
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'feedbacks_feedbackcomment' 
            AND column_name IN ('display_mode', 'nickname')
            ORDER BY column_name
        """)
        
        print("\nFinal column status:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}, nullable={row[2]}, default={row[3]}")

if __name__ == "__main__":
    try:
        ensure_feedback_columns()
        print("\n Feedback columns check completed")
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)