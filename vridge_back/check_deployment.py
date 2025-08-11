#!/usr/bin/env python
"""
Railway    
"""
import os
import sys
import django

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from projects.models import Project
from feedbacks.models import FeedBack, FeedBackComment

User = get_user_model()

def check_database_tables():
    """  """
    print("    ...")
    
    with connection.cursor() as cursor:
        # PostgreSQL   
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cursor.fetchall()
        
        print(f"\n  {len(tables)} :")
        for table in tables:
            print(f"  - {table[0]}")
    
    #   
    print("\n   :")
    print(f"  -  : {User.objects.count()}")
    print(f"  -  : {Project.objects.count()}")
    print(f"  -   : {FeedBack.objects.count()}")
    print(f"  -   : {FeedBackComment.objects.count()}")

def check_user_fields():
    """User   """
    print("\n User    ...")
    
    #    
    user = User.objects.first()
    if user:
        fields = [f.name for f in User._meta.get_fields()]
        print(f"  User   ({len(fields)}):")
        for field in sorted(fields):
            print(f"    - {field}")
    else:
        print("    .")

def check_missing_columns():
    """  """
    print("\n    ...")
    
    with connection.cursor() as cursor:
        # email_verified  
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users_user' 
            AND column_name = 'email_verified';
        """)
        
        if cursor.fetchone():
            print("   email_verified  ")
        else:
            print("   email_verified  ")
        
        #    
        important_columns = [
            ('users_user', 'nickname'),
            ('users_user', 'login_method'),
            ('projects_project', 'created'),
            ('projects_project', 'updated'),
        ]
        
        for table, column in important_columns:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND column_name = %s;
            """, [table, column])
            
            if cursor.fetchone():
                print(f"   {table}.{column} ")
            else:
                print(f"   {table}.{column} ")

if __name__ == '__main__':
    try:
        print(" Railway    ...\n")
        
        check_database_tables()
        check_user_fields()
        check_missing_columns()
        
        print("\n  !")
        
    except Exception as e:
        print(f"\n  : {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)