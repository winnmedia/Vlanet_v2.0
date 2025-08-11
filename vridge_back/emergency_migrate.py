"""
Railway  is_deleted    
Django       
: python emergency_migrate.py
"""
import os
import sys
import django
from django.core.management import call_command
from django.db import connection, transaction

# Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

def emergency_add_is_deleted_fields():
    """  is_deleted    """
    print("=== is_deleted     ===")
    
    try:
        with connection.cursor() as cursor:
            # 1.  users_user   
            print("\n1.  users_user   :")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name='users_user' 
                AND column_name IN ('is_deleted', 'deleted_at', 'can_recover', 'deletion_reason', 'recovery_deadline')
                ORDER BY column_name;
            """)
            existing_columns = cursor.fetchall()
            existing_column_names = {col[0] for col in existing_columns}
            
            print(" :")
            for col in existing_columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'} DEFAULT {col[3] or 'None'}")
            
            # 2.   
            required_fields = {
                'is_deleted': "BOOLEAN DEFAULT FALSE NOT NULL",
                'deleted_at': "TIMESTAMP NULL",
                'can_recover': "BOOLEAN DEFAULT TRUE NOT NULL", 
                'deletion_reason': "VARCHAR(200) NULL",
                'recovery_deadline': "TIMESTAMP NULL"
            }
            
            print("\n2.    ...")
            with transaction.atomic():
                for field_name, field_def in required_fields.items():
                    if field_name not in existing_column_names:
                        sql = f"ALTER TABLE users_user ADD COLUMN {field_name} {field_def}"
                        print(f"  : {sql}")
                        cursor.execute(sql)
                        print(f"   {field_name}   ")
                    else:
                        print(f"   {field_name}   ")
                        
                # 3.  
                print("\n3.   ...")
                index_sql = """
                    CREATE INDEX IF NOT EXISTS users_user_is_deleted_deleted_at_idx 
                    ON users_user (is_deleted, deleted_at)
                """
                cursor.execute(index_sql)
                print("     ")
                
        return True
        
    except Exception as e:
        print(f"\n   : {str(e)}")
        return False

def verify_is_deleted_fields():
    """   ORM  """
    print("\n4. ORM  :")
    
    try:
        from users.models import User
        
        # ORM   
        total_users = User.objects.count()
        active_users = User.objects.filter(is_deleted=False).count() 
        deleted_users = User.objects.filter(is_deleted=True).count()
        
        print(f"  -   : {total_users}")
        print(f"  -    (is_deleted=False): {active_users}")
        print(f"  -    (is_deleted=True): {deleted_users}")
        
        #  SQL 
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users_user WHERE is_deleted = FALSE")
            sql_count = cursor.fetchone()[0]
            print(f"  - SQL   : {sql_count}")
            
        print("   ORM   ")
        return True
        
    except Exception as e:
        print(f"   ORM   : {str(e)}")
        return False

def run_emergency_migration():
    """    """
    success_steps = 0
    total_steps = 3
    
    # Step 1:  
    if emergency_add_is_deleted_fields():
        success_steps += 1
    else:
        print("   .")
        return False
        
    # Step 2: ORM 
    if verify_is_deleted_fields():
        success_steps += 1
    else:
        print("ORM   .")
        
    # Step 3: Django    
    print("\n5. Django   :")
    try:
        call_command('migrate', '--fake', 'users', '0016', verbosity=2)
        call_command('migrate', '--fake', 'users', '0017', verbosity=2)
        call_command('migrate', '--fake', 'users', '0018', verbosity=2)
        print("      ")
        success_steps += 1
    except Exception as e:
        print(f"       ( ): {str(e)}")
        
    print(f"\n===    ({success_steps}/{total_steps}  ) ===")
    
    if success_steps >= 2:  #   ORM   OK
        print(" is_deleted    !")
        print(" Django     .")
        return True
    else:
        print("  .      .")
        return False

if __name__ == "__main__":
    print("VideoPlanet Railway is_deleted    ")
    print("=" * 60)
    
    success = run_emergency_migration()
    
    if success:
        print("\n  ! Railway   .")
        sys.exit(0)
    else:
        print("\n  . Railway     .")
        sys.exit(1)