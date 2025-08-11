#!/usr/bin/env python3
"""
     
Railway    .
"""
import os
import sys
import django
from django.core.management import call_command
from django.db import connection
from pathlib import Path

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings_railway'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("     ...")
print(f"   Django : {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"   : {os.environ.get('DATABASE_URL', 'SQLite ()')[:50]}...")

def check_database_connection():
    """  """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("   ")
            return True
    except Exception as e:
        print(f"   : {e}")
        return False

def ensure_migration_tables():
    """    """
    try:
        with connection.cursor() as cursor:
            # django_migrations  
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'django_migrations'
                );
            """)
            exists = cursor.fetchone()[0]
            
            if not exists:
                print("  django_migrations  .  ...")
                call_command('migrate', 'contenttypes', '--run-syncdb', verbosity=0)
                print(" django_migrations   ")
            else:
                print(" django_migrations  ")
                
    except Exception as e:
        print(f"     : {e}")
        # PostgreSQL   (SQLite )
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations';")
            if not cursor.fetchone():
                call_command('migrate', 'contenttypes', '--run-syncdb', verbosity=0)
        except:
            pass

def run_migrations_safely():
    """  """
    apps_order = [
        'contenttypes',
        'auth',
        'users',
        'projects', 
        'feedbacks',
        'video_planning',
        'video_analysis',
        'admin',
        'sessions',
    ]
    
    print("\n   :")
    
    for app in apps_order:
        try:
            print(f"\n {app}  ...")
            call_command('migrate', app, verbosity=1)
            print(f" {app} ")
        except Exception as e:
            print(f"  {app}  : {e}")
            #   
            continue
    
    #      
    try:
        print("\n    ...")
        call_command('migrate', verbosity=1)
        print("   ")
    except Exception as e:
        print(f"    : {e}")

def verify_critical_tables():
    """    """
    critical_tables = [
        'django_migrations',
        'auth_user',
        'users_user',
        'projects_project',
        'feedbacks_feedback',
    ]
    
    print("\n   :")
    all_exists = True
    
    try:
        with connection.cursor() as cursor:
            # PostgreSQL 
            for table in critical_tables:
                try:
                    cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');")
                    exists = cursor.fetchone()[0]
                    if exists:
                        print(f"    {table}")
                    else:
                        print(f"    {table} - ")
                        all_exists = False
                except:
                    # SQLite 
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
                    if cursor.fetchone():
                        print(f"    {table}")
                    else:
                        print(f"    {table} - ")
                        all_exists = False
                        
    except Exception as e:
        print(f"   : {e}")
        all_exists = False
    
    return all_exists

def create_missing_columns():
    """  """
    column_fixes = [
        # (, , SQL)
        ('projects_project', 'development_framework', 
         "ALTER TABLE projects_project ADD COLUMN development_framework VARCHAR(50) DEFAULT 'React';"),
        ('feedbacks_feedback', 'priority', 
         "ALTER TABLE feedbacks_feedback ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';"),
        ('feedbacks_feedback', 'category', 
         "ALTER TABLE feedbacks_feedback ADD COLUMN category VARCHAR(50) DEFAULT 'general';"),
    ]
    
    print("\n     :")
    
    with connection.cursor() as cursor:
        for table, column, sql in column_fixes:
            try:
                #    
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    AND column_name = '{column}';
                """)
                
                if not cursor.fetchone():
                    print(f"     {table}.{column}  -  ...")
                    cursor.execute(sql)
                    print(f"    {table}.{column}  ")
                else:
                    print(f"    {table}.{column}  ")
                    
            except Exception as e:
                print(f"    {table}.{column}  : {e}")

def main():
    """  """
    try:
        # Django 
        django.setup()
        print(" Django  \n")
        
        # 1.   
        if not check_database_connection():
            print("\n   .  .")
            return False
        
        # 2.   
        ensure_migration_tables()
        
        # 3.  
        run_migrations_safely()
        
        # 4.   
        if verify_critical_tables():
            print("\n    .")
        else:
            print("\n    .")
            
        # 5.   
        create_missing_columns()
        
        print("\n   !")
        return True
        
    except Exception as e:
        print(f"\n   : {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)